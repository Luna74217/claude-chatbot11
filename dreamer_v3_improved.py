"""
Dreamer V3 + Hierarchical PPO + Curiosity/Empowerment/Meta-gradient (Slim)
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical, kl_divergence
import numpy as np
from collections import defaultdict, deque
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DreamerConfig:
    obs_dim: int = 779
    embed_dim: int = 1024
    feature_dim: int = 256
    action_dim: int = 5
    deter_dim: int = 256
    categ: int = 32
    group: int = 32
    stoch_dim: int = 1024
    num_options: int = 8
    option_embed_dim: int = 64
    empowerment_k: int = 8
    hash_mod: int = 100_000
    batch_size: int = 16
    seq_len: int = 64
    buffer_size: int = 1_000_000
    initial_episodes: int = 10
    collect_interval: int = 100
    log_interval: int = 100
    checkpoint_interval: int = 10000
    world_lr: float = 6e-4
    actor_lr: float = 3e-4
    intrinsic_lr: float = 3e-4
    kl_scale: float = 1.0
    kl_balance: float = 0.8
    free_nats: float = 3.0
    clip_ratio: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    use_wandb: bool = True
    checkpoint_dir: str = "./checkpoints"
    device: str = "auto"
    def __post_init__(self):
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        assert self.stoch_dim == self.categ * self.group
        Path(self.checkpoint_dir).mkdir(exist_ok=True)

def one_hot_from_logits(logits: torch.Tensor) -> torch.Tensor:
    y_soft = torch.softmax(logits, dim=-1)
    index = y_soft.max(-1, keepdim=True)[1]
    y_hard = torch.zeros_like(logits).scatter_(-1, index, 1.0)
    return (y_hard - y_soft).detach() + y_soft

def symlog(x: torch.Tensor) -> torch.Tensor:
    return torch.sign(x) * torch.log(torch.abs(x) + 1)

def symexp(x: torch.Tensor) -> torch.Tensor:
    return torch.sign(x) * (torch.exp(torch.abs(x)) - 1)

class SequenceReplayBuffer:
    def __init__(self, capacity: int = 1_000_000, seq_len: int = 64):
        self.capacity = capacity
        self.seq_len = seq_len
        self.buffer = deque(maxlen=capacity)
    def add_episode(self, episode: dict):
        T = len(episode["observations"])
        if T < self.seq_len:
            return
        stride = self.seq_len // 2
        for i in range(0, T - self.seq_len + 1, stride):
            seq = {k: v[i:i + self.seq_len] if len(v) == T else v[i:i + self.seq_len - 1] for k, v in episode.items()}
            self.buffer.append(seq)
    def sample(self, batch_size: int) -> dict:
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        batch = defaultdict(list)
        for idx in indices:
            seq = self.buffer[idx]
            for k, v in seq.items():
                batch[k].append(torch.tensor(v, dtype=torch.float32))
        return {k: torch.stack(v) for k, v in batch.items()}
    def __len__(self):
        return len(self.buffer)

class GradientMonitor:
    """그래디언트 모니터링 유틸리티."""
    
    def __init__(self, model: nn.Module):
        self.model = model
        self.grad_norms = []
        
    def compute_grad_norm(self) -> float:
        """현재 그래디언트 노름 계산."""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        return total_norm ** (1. / 2)
    
    def log_grad_norms(self, step: int):
        """그래디언트 노름 로깅."""
        grad_norm = self.compute_grad_norm()
        self.grad_norms.append(grad_norm)
        
        if len(self.grad_norms) % 100 == 0:
            avg_norm = np.mean(self.grad_norms[-100:])
            logger.info(f"Step {step}: Avg grad norm = {avg_norm:.4f}")

class DreamerV3Loss(nn.Module):
    """개선된 Dreamer V3 손실 함수."""
    
    def __init__(self, config: DreamerConfig):
        super().__init__()
        self.config = config
        
    def reconstruction_loss(
        self,
        obs_true: torch.Tensor,
        obs_pred: torch.Tensor
    ) -> torch.Tensor:
        """관찰 재구성 손실."""
        return F.mse_loss(obs_pred, obs_true, reduction='none').sum(-1).mean()
    
    def kl_loss(
        self,
        post_logits: torch.Tensor,
        prior_logits: torch.Tensor
    ) -> torch.Tensor:
        """KL 발산 손실."""
        B, T = post_logits.shape[:2]
        
        # 카테고리별로 재구성
        post_logits = post_logits.view(B, T, self.config.group, self.config.categ)
        prior_logits = prior_logits.view(B, T, self.config.group, self.config.categ)
        
        # 분포 생성
        post_dist = Categorical(logits=post_logits)
        prior_dist = Categorical(logits=prior_logits)
        
        # 그룹별 KL 계산
        kl = kl_divergence(post_dist, prior_dist).sum(-1)  # (B, T)
        
        # Free nats 적용
        kl = torch.maximum(kl, torch.tensor(self.config.free_nats, device=kl.device))
        
        # Posterior와 prior 그래디언트 균형
        kl_post = (1 - self.config.kl_balance) * kl
        kl_prior = self.config.kl_balance * kl.detach()
        
        return (kl_post + kl_prior).mean() * self.config.kl_scale
    
    def reward_loss(
        self,
        reward_true: torch.Tensor,
        reward_pred: torch.Tensor
    ) -> torch.Tensor:
        """보상 예측 손실."""
        target = symlog(reward_true)
        return F.mse_loss(reward_pred, target)
    
    def continue_loss(
        self,
        continue_true: torch.Tensor,
        continue_pred: torch.Tensor
    ) -> torch.Tensor:
        """연속성 예측 손실."""
        return F.binary_cross_entropy(continue_pred, continue_true.float())

class PPOLoss(nn.Module):
    """개선된 PPO 손실 함수."""
    
    def __init__(self, config: DreamerConfig):
        super().__init__()
        self.config = config
        
    def policy_loss(
        self,
        action_logits: torch.Tensor,
        actions: torch.Tensor,
        advantages: torch.Tensor,
        old_log_probs: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """클리핑된 PPO 정책 손실."""
        # 현재 로그 확률
        dist = Categorical(logits=action_logits)
        log_probs = dist.log_prob(actions)
        
        # 비율 계산
        ratio = torch.exp(log_probs - old_log_probs)
        
        # 클리핑된 목적 함수
        obj = ratio * advantages
        obj_clipped = torch.clamp(ratio, 1 - self.config.clip_ratio, 1 + self.config.clip_ratio) * advantages
        
        # 손실
        policy_loss = -torch.min(obj, obj_clipped).mean()
        
        # 엔트로피
        entropy = dist.entropy().mean()
        
        # 통계
        with torch.no_grad():
            approx_kl = (old_log_probs - log_probs).mean()
            clip_frac = ((ratio - 1).abs() > self.config.clip_ratio).float().mean()
            
        stats = {
            "policy_loss": policy_loss.item(),
            "entropy": entropy.item(),
            "approx_kl": approx_kl.item(),
            "clip_frac": clip_frac.item()
        }
        
        return policy_loss - self.config.entropy_coef * entropy, stats
    
    def value_loss(
        self,
        values: torch.Tensor,
        returns: torch.Tensor,
        old_values: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """가치 함수 손실."""
        if old_values is not None:
            # 클리핑된 가치 손실
            v_clipped = old_values + torch.clamp(
                values - old_values, -self.config.clip_ratio, self.config.clip_ratio
            )
            v_loss = torch.max(
                F.mse_loss(values, returns, reduction='none'),
                F.mse_loss(v_clipped, returns, reduction='none')
            ).mean()
        else:
            v_loss = F.mse_loss(values, returns)
            
        return v_loss * self.config.value_coef

class DreamerV3Trainer:
    """개선된 Dreamer V3 트레이너."""
    
    def __init__(
        self,
        model: nn.Module,
        env_fn: callable,
        config: DreamerConfig
    ):
        self.model = model
        self.env_fn = env_fn
        self.config = config
        
        # 디바이스 설정
        self.device = torch.device(config.device)
        self.model.to(self.device)
        
        # 리플레이 버퍼
        self.replay_buffer = SequenceReplayBuffer(
            capacity=config.buffer_size,
            seq_len=config.seq_len
        )
        
        # 손실 함수
        self.dreamer_loss = DreamerV3Loss(config)
        self.ppo_loss = PPOLoss(config)
        
        # 옵티마이저
        self.world_optimizer = torch.optim.Adam(
            self.model.world_model.parameters(),
            lr=config.world_lr
        )
        
        self.actor_optimizer = torch.optim.Adam(
            self.model.policy.parameters(),
            lr=config.actor_lr
        )
        
        self.intrinsic_optimizer = torch.optim.Adam(
            list(self.model.icm.parameters()) + 
            list(self.model.empowerment.parameters()),
            lr=config.intrinsic_lr
        )
        
        # 그래디언트 모니터
        self.grad_monitor = GradientMonitor(self.model)
        
        # 학습 상태
        self.global_step = 0
        self.episodes_collected = 0
        self.best_return = float('-inf')
        
        # 메트릭 저장
        self.metrics_history = defaultdict(list)
        
    def collect_episode(self) -> Dict[str, np.ndarray]:
        """현재 정책으로 에피소드 수집."""
        env = self.env_fn()
        obs, _ = env.reset()
        
        episode = defaultdict(list)
        h = torch.zeros(1, self.config.deter_dim, device=self.device)
        stoch = torch.zeros(1, self.config.stoch_dim, device=self.device)
        option = None
        
        done = False
        step_count = 0
        max_steps = 1000  # 안전장치
        
        while not done and step_count < max_steps:
            # 관찰 처리
            obs_tensor = torch.tensor(obs, device=self.device).unsqueeze(0)
            
            with torch.no_grad():
                # 월드 모델 스텝
                embed = self.model.world_model.rssm.embed(obs_tensor)
                result = self.model.world_model.rssm.dynamics_step(embed, h, stoch)
                h = result["h"]
                stoch = result["stoch"]
                
                # 정책 스텝
                state = torch.cat([h, stoch], dim=-1)
                policy_out = self.model.policy(state, option)
                
                # 옵션 전환
                if option is None or torch.bernoulli(policy_out["term_prob"]).item():
                    option_dist = Categorical(policy_out["option_probs"])
                    option = option_dist.sample()
                
                # 액션 샘플링
                action_dist = Categorical(policy_out["action_probs"])
                action = action_dist.sample()
            
            # 환경 스텝
            try:
                next_obs, reward, terminated, truncated, info = env.step(action.item())
                done = terminated or truncated
            except Exception as e:
                logger.error(f"Environment step failed: {e}")
                break
            
            # 전환 저장
            episode["observations"].append(obs)
            episode["actions"].append(action.item())
            episode["rewards"].append(reward)
            episode["continues"].append(1.0 - float(terminated))
            episode["options"].append(option.item())
            
            obs = next_obs
            step_count += 1
        
        # 배열로 변환
        episode = {k: np.array(v) for k, v in episode.items()}
        
        # 다음 관찰 추가
        episode["next_observations"] = np.concatenate([
            episode["observations"][1:],
            [obs]
        ])
        
        env.close()
        return episode
    
    def train_world_model(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """월드 모델 훈련."""
        obs_seq = batch["observations"].to(self.device)
        rewards = batch["rewards"].to(self.device)
        continues = batch["continues"].to(self.device)
        
        # 순전파
        model_out = self.model.world_model(obs_seq)
        
        # 손실 계산
        recon_loss = self.dreamer_loss.reconstruction_loss(
            obs_seq, model_out["obs_pred"]
        )
        
        kl_loss = self.dreamer_loss.kl_loss(
            model_out["post_logits"], model_out["prior_logits"]
        )
        
        reward_loss = self.dreamer_loss.reward_loss(
            rewards, model_out["reward_pred"]
        )
        
        continue_loss = self.dreamer_loss.continue_loss(
            continues, model_out["continue_pred"]
        )
        
        # 총 손실
        total_loss = recon_loss + kl_loss + reward_loss + continue_loss
        
        # 역전파
        self.world_optimizer.zero_grad()
        total_loss.backward()
        nn.utils.clip_grad_norm_(self.model.world_model.parameters(), 100.0)
        self.world_optimizer.step()
        
        return {
            "world/recon_loss": recon_loss.item(),
            "world/kl_loss": kl_loss.item(),
            "world/reward_loss": reward_loss.item(),
            "world/continue_loss": continue_loss.item(),
            "world/total_loss": total_loss.item()
        }
    
    def train_policy(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """정책 훈련."""
        obs_seq = batch["observations"].to(self.device)
        
        with torch.no_grad():
            # 월드 모델에서 초기 상태 얻기
            model_out = self.model.world_model(obs_seq[:, :1])
            initial_state = {
                "h": model_out["hs"][:, -1],
                "stoch": model_out["stochs"][:, -1]
            }
        
        # 상상 롤아웃
        trajectory = self.model.imagine_rollout(initial_state, horizon=15)
        
        # 리턴 계산
        returns = self.compute_returns(
            trajectory["rewards"],
            trajectory["continues"],
            trajectory["values"]
        )
        
        # 어드밴티지
        advantages = returns - torch.stack(trajectory["values"])
        
        # 정책 손실
        states = torch.stack(trajectory["states"][:-1])
        actions = torch.stack(trajectory["actions"])
        
        # 현재 정책 출력
        policy_out = self.model.policy(states.reshape(-1, states.shape[-1]))
        action_logits = policy_out["action_logits"].reshape(states.shape[0], states.shape[1], -1)
        values = policy_out["action_value"].reshape(states.shape[0], states.shape[1])
        
        # 이전 로그 확률 (실제로는 롤아웃에서 저장해야 함)
        with torch.no_grad():
            dist = Categorical(logits=action_logits)
            old_log_probs = dist.log_prob(actions)
        
        policy_loss, policy_stats = self.ppo_loss.policy_loss(
            action_logits, actions, advantages, old_log_probs
        )
        
        value_loss = self.ppo_loss.value_loss(values, returns)
        
        # 총 손실
        total_loss = policy_loss + value_loss
        
        # 역전파
        self.actor_optimizer.zero_grad()
        total_loss.backward()
        nn.utils.clip_grad_norm_(self.model.policy.parameters(), 0.5)
        self.actor_optimizer.step()
        
        # 메트릭
        metrics = {f"policy/{k}": v for k, v in policy_stats.items()}
        metrics["policy/value_loss"] = value_loss.item()
        metrics["policy/total_loss"] = total_loss.item()
        
        return metrics
    
    def train_intrinsic(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """내재적 보상 모듈 훈련."""
        obs_seq = batch["observations"].to(self.device)
        actions = batch["actions"].to(self.device)
        
        # ICM 손실
        icm_losses = []
        for t in range(obs_seq.shape[1] - 1):
            _, loss_dict = self.model.icm(
                obs_seq[:, t], obs_seq[:, t + 1], actions[:, t]
            )
            icm_losses.append(loss_dict["total"])
        
        icm_loss = torch.stack(icm_losses).mean()
        
        # Empowerment 손실
        emp_losses = []
        for t in range(max(0, obs_seq.shape[1] - self.config.empowerment_k - 1)):
            obs_window = obs_seq[:, t:t + self.config.empowerment_k + 1]
            act_window = actions[:, t:t + self.config.empowerment_k]
            _, loss_dict = self.model.empowerment(obs_window, act_window)
            emp_losses.append(loss_dict["empower_loss"])
        
        emp_loss = torch.stack(emp_losses).mean() if emp_losses else torch.tensor(0.0)
        
        # 총 손실
        total_loss = icm_loss + emp_loss
        
        # 역전파
        self.intrinsic_optimizer.zero_grad()
        total_loss.backward()
        nn.utils.clip_grad_norm_(
            list(self.model.icm.parameters()) + 
            list(self.model.empowerment.parameters()),
            1.0
        )
        self.intrinsic_optimizer.step()
        
        return {
            "intrinsic/icm_loss": icm_loss.item(),
            "intrinsic/empowerment_loss": emp_loss.item(),
            "intrinsic/total_loss": total_loss.item()
        }
    
    def compute_returns(
        self,
        rewards: List[torch.Tensor],
        continues: List[torch.Tensor],
        values: List[torch.Tensor],
        gamma: float = 0.99,
        lambda_: float = 0.95
    ) -> torch.Tensor:
        """람다 리턴 계산."""
        returns = []
        R = values[-1] if values else 0
        
        for r, c, v in zip(reversed(rewards), reversed(continues), reversed(values[:-1])):
            R = r + gamma * c * (lambda_ * R + (1 - lambda_) * v)
            returns.append(R)
            
        returns.reverse()
        return torch.stack(returns)
    
    def train_step(self) -> Dict[str, float]:
        """단일 훈련 스텝."""
        # 배치 샘플링
        batch = self.replay_buffer.sample(self.config.batch_size)
        
        # 컴포넌트 훈련
        world_metrics = self.train_world_model(batch)
        policy_metrics = self.train_policy(batch)
        intrinsic_metrics = self.train_intrinsic(batch)
        
        # 메타 그래디언트 스텝
        total_loss = sum([
            world_metrics["world/total_loss"],
            policy_metrics["policy/total_loss"],
            intrinsic_metrics["intrinsic/total_loss"]
        ])
        
        grad_norm = self.grad_monitor.compute_grad_norm()
        
        meta_out = self.model.meta_optimizer(
            torch.tensor(total_loss),
            torch.tensor(grad_norm),
            self.global_step
        )
        
        # 학습률 업데이트
        for param_group in self.world_optimizer.param_groups:
            param_group['lr'] = meta_out['lr'].item()
        for param_group in self.actor_optimizer.param_groups:
            param_group['lr'] = meta_out['lr'].item()
        
        # 메트릭 결합
        metrics = {}
        metrics.update(world_metrics)
        metrics.update(policy_metrics)
        metrics.update(intrinsic_metrics)
        metrics.update({
            "meta/lr": meta_out['lr'].item(),
            "meta/lr_mult": meta_out['lr_mult'].item(),
            "meta/grad_norm": grad_norm
        })
        
        # 메트릭 히스토리 저장
        for k, v in metrics.items():
            self.metrics_history[k].append(v)
        
        self.global_step += 1
        return metrics
    
    def train(self, num_steps: int = 1_000_000):
        """메인 훈련 루프."""
        # Wandb 초기화
        if self.config.use_wandb:
            wandb.init(
                project="dreamer-v3-hierarchical-improved",
                config=self.config.__dict__
            )
        
        # 초기 에피소드 수집
        logger.info("초기 에피소드 수집 중...")
        while len(self.replay_buffer) < self.config.initial_episodes:
            try:
                episode = self.collect_episode()
                self.replay_buffer.add_episode(episode)
                self.episodes_collected += 1
                
                if self.episodes_collected % 10 == 0:
                    logger.info(f"수집된 에피소드: {self.episodes_collected}")
            except Exception as e:
                logger.error(f"에피소드 수집 실패: {e}")
                continue
        
        # 훈련 루프
        logger.info("훈련 시작...")
        
        for step in range(num_steps):
            try:
                # 새 에피소드 수집
                if step % self.config.collect_interval == 0:
                    episode = self.collect_episode()
                    self.replay_buffer.add_episode(episode)
                    self.episodes_collected += 1
                    
                    # 에피소드 통계 로깅
                    ep_return = sum(episode["rewards"])
                    ep_length = len(episode["rewards"])
                    
                    # 최고 성능 추적
                    if ep_return > self.best_return:
                        self.best_return = ep_return
                        self.save_checkpoint("best_model.pt")
                    
                    if self.config.use_wandb:
                        wandb.log({
                            "episode/return": ep_return,
                            "episode/length": ep_length,
                            "episode/num_episodes": self.episodes_collected,
                            "episode/best_return": self.best_return
                        }, step=self.global_step)
                
                # 훈련 스텝
                metrics = self.train_step()
                
                # 로깅
                if step % self.config.log_interval == 0:
                    logger.info(f"Step {step}: {metrics}")
                    
                    if self.config.use_wandb:
                        wandb.log(metrics, step=self.global_step)
                
                # 체크포인트
                if step % self.config.checkpoint_interval == 0:
                    self.save_checkpoint(f"checkpoint_{step}.pt")
                    
                    # 버퍼 통계 로깅
                    buffer_stats = self.replay_buffer.get_stats()
                    logger.info(f"Buffer stats: {buffer_stats}")
                
            except Exception as e:
                logger.error(f"훈련 스텝 실패: {e}")
                continue
        
        logger.info("훈련 완료!")
        if self.config.use_wandb:
            wandb.finish()
    
    def save_checkpoint(self, filename: str):
        """모델 체크포인트 저장."""
        checkpoint = {
            "model_state": self.model.state_dict(),
            "world_optimizer": self.world_optimizer.state_dict(),
            "actor_optimizer": self.actor_optimizer.state_dict(),
            "intrinsic_optimizer": self.intrinsic_optimizer.state_dict(),
            "global_step": self.global_step,
            "episodes_collected": self.episodes_collected,
            "best_return": self.best_return,
            "config": self.config,
            "metrics_history": dict(self.metrics_history)
        }
        
        path = Path(self.config.checkpoint_dir) / filename
        torch.save(checkpoint, path)
        logger.info(f"체크포인트 저장: {filename}")
    
    def load_checkpoint(self, filename: str):
        """체크포인트 로드."""
        path = Path(self.config.checkpoint_dir) / filename
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint["model_state"])
        self.world_optimizer.load_state_dict(checkpoint["world_optimizer"])
        self.actor_optimizer.load_state_dict(checkpoint["actor_optimizer"])
        self.intrinsic_optimizer.load_state_dict(checkpoint["intrinsic_optimizer"])
        
        self.global_step = checkpoint["global_step"]
        self.episodes_collected = checkpoint["episodes_collected"]
        self.best_return = checkpoint.get("best_return", float('-inf'))
        
        # 메트릭 히스토리 복원
        if "metrics_history" in checkpoint:
            self.metrics_history = defaultdict(list, checkpoint["metrics_history"])
        
        logger.info(f"체크포인트 로드: {filename}")

def create_env():
    """환경 인스턴스 생성."""
    # 여기에 환경을 import하세요
    # from envs.emotion_world import EmotionWorld
    # return EmotionWorld()
    
    # 테스트용 플레이스홀더
    import gym
    return gym.make("CartPole-v1")

def main():
    parser = argparse.ArgumentParser(description="Dreamer V3 개선된 훈련")
    parser.add_argument("--config", type=str, default="configs/default.json")
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=1_000_000)
    args = parser.parse_args()
    
    # 설정 로드
    if Path(args.config).exists():
        with open(args.config) as f:
            config_dict = json.load(f)
        config = DreamerConfig(**config_dict)
    else:
        config = DreamerConfig()
    
    # 디바이스 설정
    if args.device != "auto":
        config.device = args.device
    
    # 시드 설정
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # 모델 생성 (Part 1에서 정의된 모델 사용)
    # model = DreamerV3HierarchicalPPO()
    
    # 체크포인트 로드
    if args.checkpoint:
        # checkpoint = torch.load(args.checkpoint)
        # model.load_state_dict(checkpoint["model_state"])
        logger.info(f"체크포인트 로드: {args.checkpoint}")
    
    # 트레이너 생성
    # trainer = DreamerV3Trainer(
    #     model=model,
    #     env_fn=create_env,
    #     config=config
    # )
    
    # 훈련
    # trainer.train(num_steps=args.steps)

if __name__ == "__main__":
    main() 