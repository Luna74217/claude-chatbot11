"""
Dreamer V3 멀티모달 확장 (Slim)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import TransformerEncoder, TransformerEncoderLayer
from typing import Dict, Tuple, Optional
import numpy as np
from einops import repeat
from dataclasses import dataclass

@dataclass
class ModalityConfig:
    name: str
    input_shape: Tuple[int, ...]
    embed_dim: int
    encoder_type: str
    decoder_type: str
    loss_weight: float = 1.0
    loss_type: str = 'mse'

MODALITY_CONFIGS = {
    "image": ModalityConfig("image", (3, 64, 64), 512, "cnn", "cnn"),
    "text": ModalityConfig("text", (512,), 384, "transformer", "transformer", 0.5, "ce"),
    "audio": ModalityConfig("audio", (1, 16000), 256, "audio", "audio", 0.8, "mse"),
    "vector": ModalityConfig("vector", (779,), 256, "mlp", "mlp")
}

class CNNEncoder(nn.Module):
    def __init__(self, config: ModalityConfig):
        super().__init__()
        c, h, w = config.input_shape
        self.conv_layers = nn.Sequential(
            nn.Conv2d(c, 32, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(32, 64, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(128, 256, 4, 2, 1), nn.ReLU(),
        )
        dummy = torch.zeros(1, c, h, w)
        self.flatten_size = self.conv_layers(dummy).numel()
        self.proj = nn.Sequential(
            nn.Linear(self.flatten_size, config.embed_dim),
            nn.LayerNorm(config.embed_dim)
        )
    def forward(self, x):
        features = self.conv_layers(x)
        features = features.view(features.size(0), -1)
        return self.proj(features)

class TransformerTextEncoder(nn.Module):
    def __init__(self, config: ModalityConfig, vocab_size: int = 30000):
        super().__init__()
        self.token_embed = nn.Embedding(vocab_size, config.embed_dim)
        self.pos_embed = nn.Parameter(torch.randn(1, config.input_shape[0], config.embed_dim))
        encoder_layer = TransformerEncoderLayer(
            d_model=config.embed_dim, nhead=8, dim_feedforward=config.embed_dim * 4, dropout=0.1, batch_first=True)
        self.transformer = TransformerEncoder(encoder_layer, num_layers=4)
        self.pool = nn.Sequential(nn.Linear(config.embed_dim, config.embed_dim), nn.Tanh())
    def forward(self, x, mask: Optional[torch.Tensor] = None):
        embeds = self.token_embed(x) + self.pos_embed[:, :x.size(1)]
        encoded = self.transformer(embeds, src_key_padding_mask=mask)
        if mask is not None:
            mask_expanded = mask.unsqueeze(-1).expand_as(encoded)
            sum_embeds = (encoded * ~mask_expanded).sum(dim=1)
            count = (~mask).sum(dim=1, keepdim=True).float()
            pooled = sum_embeds / count.clamp(min=1)
        else:
            pooled = encoded.mean(dim=1)
        return self.pool(pooled)

class AudioEncoder(nn.Module):
    def __init__(self, config: ModalityConfig):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv1d(1, 32, 25, 5), nn.ReLU(),
            nn.Conv1d(32, 64, 25, 5), nn.ReLU(),
            nn.Conv1d(64, 128, 10, 2), nn.ReLU(),
            nn.Conv1d(128, 256, 10, 2), nn.ReLU(),
            nn.AdaptiveAvgPool1d(32)
        )
        self.proj = nn.Sequential(
            nn.Linear(256 * 32, config.embed_dim),
            nn.LayerNorm(config.embed_dim)
        )
    def forward(self, x):
        features = self.conv_layers(x)
        features = features.view(features.size(0), -1)
        return self.proj(features)

class MLPEncoder(nn.Module):
    def __init__(self, config: ModalityConfig):
        super().__init__()
        input_dim = config.input_shape[0]
        self.net = nn.Sequential(
            nn.Linear(input_dim, 1024), nn.ReLU(),
            nn.Linear(1024, 512), nn.ReLU(),
            nn.Linear(512, config.embed_dim), nn.LayerNorm(config.embed_dim)
        )
    def forward(self, x):
        return self.net(x)

# ============================================================================
# 모달리티 디코더
# ============================================================================

class CNNDecoder(nn.Module):
    """이미지 재구성용 컨볼루션 디코더."""
    
    def __init__(self, config: ModalityConfig, latent_dim: int):
        super().__init__()
        self.config = config
        c, h, w = config.input_shape
        
        # 투영 후 초기 형태 계산
        self.init_h = h // 16
        self.init_w = w // 16
        self.init_c = 256
        
        self.proj = nn.Sequential(
            nn.Linear(latent_dim, self.init_h * self.init_w * self.init_c),
            nn.ReLU()
        )
        
        self.deconv_layers = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(32, c, 4, 2, 1)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """순전파: (B, latent_dim) -> (B, C, H, W)"""
        x = self.proj(x)
        x = x.view(-1, self.init_c, self.init_h, self.init_w)
        return self.deconv_layers(x)

class TransformerTextDecoder(nn.Module):
    """텍스트 생성용 트랜스포머 디코더."""
    
    def __init__(self, config: ModalityConfig, latent_dim: int, vocab_size: int = 30000):
        super().__init__()
        self.config = config
        self.vocab_size = vocab_size
        self.max_len = config.input_shape[0]
        
        # 잠재 공간을 시퀀스로 투영
        self.latent_proj = nn.Linear(latent_dim, config.embed_dim * 8)
        
        # 트랜스포머 디코더
        decoder_layer = TransformerEncoderLayer(
            d_model=config.embed_dim,
            nhead=8,
            dim_feedforward=config.embed_dim * 4,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = TransformerEncoder(decoder_layer, num_layers=4)
        
        # 출력 투영
        self.out_proj = nn.Linear(config.embed_dim, vocab_size)
        
        # 학습된 쿼리
        self.queries = nn.Parameter(torch.randn(1, self.max_len, config.embed_dim))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """순전파: (B, latent_dim) -> (B, L, vocab_size)"""
        B = x.size(0)
        
        # 잠재 공간을 초기 시퀀스로 투영
        latent_seq = self.latent_proj(x).view(B, 8, -1)
        
        # 쿼리와 결합
        queries = repeat(self.queries, '1 l d -> b l d', b=B)
        decoder_input = torch.cat([latent_seq, queries], dim=1)[:, :self.max_len]
        
        # 디코딩
        decoded = self.transformer(decoder_input)
        return self.out_proj(decoded)

class AudioDecoder(nn.Module):
    """오디오 재구성용 1D CNN 디코더."""
    
    def __init__(self, config: ModalityConfig, latent_dim: int):
        super().__init__()
        self.config = config
        
        self.proj = nn.Sequential(
            nn.Linear(latent_dim, 256 * 125),
            nn.ReLU()
        )
        
        self.deconv_layers = nn.Sequential(
            nn.ConvTranspose1d(256, 128, 10, 2), nn.ReLU(),
            nn.ConvTranspose1d(128, 64, 10, 2), nn.ReLU(),
            nn.ConvTranspose1d(64, 32, 25, 5), nn.ReLU(),
            nn.ConvTranspose1d(32, 1, 25, 5),
            nn.Tanh()  # 오디오는 [-1, 1] 범위
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """순전파: (B, latent_dim) -> (B, 1, L)"""
        x = self.proj(x).view(-1, 256, 125)
        return self.deconv_layers(x)

class MLPDecoder(nn.Module):
    """벡터 관찰용 MLP 디코더."""
    
    def __init__(self, config: ModalityConfig, latent_dim: int):
        super().__init__()
        self.config = config
        output_dim = config.input_shape[0]
        
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, output_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """순전파: (B, latent_dim) -> (B, D)"""
        return self.net(x)

# ============================================================================
# 멀티모달 퓨전
# ============================================================================

class MultimodalFusion(nn.Module):
    """여러 모달리티 임베딩을 결합하는 퓨전 모듈."""
    
    def __init__(self, modality_dims: Dict[str, int], fusion_dim: int = 1024):
        super().__init__()
        self.modality_dims = modality_dims
        self.fusion_dim = fusion_dim
        
        # 모달리티별 투영
        self.projections = nn.ModuleDict({
            name: nn.Linear(dim, fusion_dim)
            for name, dim in modality_dims.items()
        })
        
        # 교차 모달리티 어텐션
        self.cross_attention = nn.MultiheadAttention(
            fusion_dim, num_heads=8, batch_first=True
        )
        
        # 퓨전 네트워크
        self.fusion_net = nn.Sequential(
            nn.Linear(fusion_dim * len(modality_dims), fusion_dim),
            nn.ReLU(),
            nn.Linear(fusion_dim, fusion_dim),
            nn.LayerNorm(fusion_dim)
        )
        
        # 모달리티 중요도 가중치
        self.importance = nn.Parameter(torch.ones(len(modality_dims)))
        
    def forward(self, embeddings: Dict[str, torch.Tensor]) -> torch.Tensor:
        """여러 모달리티 임베딩 퓨전."""
        # 각 모달리티 투영
        projected = {}
        for name, embed in embeddings.items():
            if name in self.projections:
                projected[name] = self.projections[name](embed)
        
        # 교차 어텐션을 위해 스택
        stacked = torch.stack(list(projected.values()), dim=1)  # (B, M, D)
        
        # 모달리티 간 셀프 어텐션
        attended, _ = self.cross_attention(stacked, stacked, stacked)
        
        # 중요도 가중치 적용
        importance = F.softmax(self.importance, dim=0)
        weighted = attended * importance.view(1, -1, 1)
        
        # 연결 및 퓨전
        concat = weighted.view(weighted.size(0), -1)
        fused = self.fusion_net(concat)
        
        return fused

# ============================================================================
# 멀티모달 RSSM
# ============================================================================

class MultimodalRSSM(nn.Module):
    """멀티모달 관찰을 위한 확장된 RSSM."""
    
    def __init__(self, modality_configs: Dict[str, ModalityConfig]):
        super().__init__()
        self.modality_configs = modality_configs
        
        # 각 모달리티에 대한 인코더 생성
        self.encoders = nn.ModuleDict()
        for name, config in modality_configs.items():
            if config.encoder_type == "cnn":
                self.encoders[name] = CNNEncoder(config)
            elif config.encoder_type == "transformer":
                self.encoders[name] = TransformerTextEncoder(config)
            elif config.encoder_type == "audio":
                self.encoders[name] = AudioEncoder(config)
            elif config.encoder_type == "mlp":
                self.encoders[name] = MLPEncoder(config)
        
        # 멀티모달 퓨전
        modality_dims = {name: config.embed_dim for name, config in modality_configs.items()}
        self.fusion = MultimodalFusion(modality_dims, fusion_dim=1024)
        
        # RSSM 컴포넌트
        self.gru = nn.GRUCell(1024 + 1024, 256)  # 1024는 stoch_dim
        self.fc_prior = nn.Linear(256, 1024)
        self.fc_post = nn.Linear(256 + 1024, 1024)
        
        # 각 모달리티에 대한 디코더 생성
        self.decoders = nn.ModuleDict()
        latent_dim = 256 + 1024  # deter_dim + stoch_dim
        
        for name, config in modality_configs.items():
            if config.decoder_type == "cnn":
                self.decoders[name] = CNNDecoder(config, latent_dim)
            elif config.decoder_type == "transformer":
                self.decoders[name] = TransformerTextDecoder(config, latent_dim)
            elif config.decoder_type == "audio":
                self.decoders[name] = AudioDecoder(config, latent_dim)
            elif config.decoder_type == "mlp":
                self.decoders[name] = MLPDecoder(config, latent_dim)
    
    def encode_observation(self, obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """멀티모달 관찰을 통합 임베딩으로 인코딩."""
        embeddings = {}
        
        for name, encoder in self.encoders.items():
            if name in obs:
                # 다른 모달리티 처리
                if name == "text" and "text_mask" in obs:
                    embeddings[name] = encoder(obs[name], obs["text_mask"])
                else:
                    embeddings[name] = encoder(obs[name])
        
        # 임베딩 퓨전
        fused = self.fusion(embeddings)
        return fused
    
    def decode_state(self, h: torch.Tensor, stoch: torch.Tensor) -> Dict[str, torch.Tensor]:
        """잠재 상태를 멀티모달 관찰로 디코딩."""
        state = torch.cat([h, stoch], dim=-1)
        reconstructions = {}
        
        for name, decoder in self.decoders.items():
            reconstructions[name] = decoder(state)
            
        return reconstructions
    
    def dynamics_step(
        self,
        obs: Dict[str, torch.Tensor],
        h_prev: torch.Tensor,
        stoch_prev: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """멀티모달 입력으로 단일 다이나믹스 스텝."""
        # 관찰 인코딩
        embed = self.encode_observation(obs)
        
        # GRU 스텝
        gru_in = torch.cat([embed, stoch_prev], dim=-1)
        h = self.gru(gru_in, h_prev)
        
        # Prior와 posterior 계산
        prior_logits = self.fc_prior(h)
        prior_stoch = self._logits_to_stoch(prior_logits)
        
        post_logits = self.fc_post(torch.cat([h, embed], dim=-1))
        stoch = self._logits_to_stoch(post_logits)
        
        return {
            "embed": embed,
            "h": h,
            "stoch": stoch,
            "prior_logits": prior_logits,
            "post_logits": post_logits,
            "prior_stoch": prior_stoch
        }
    
    def _logits_to_stoch(self, logits: torch.Tensor) -> torch.Tensor:
        """로짓을 확률적 상태로 변환."""
        B = logits.size(0)
        logits = logits.view(B, 32, 32)  # group=32, categ=32
        stoch = self._one_hot_from_logits(logits)
        return stoch.view(B, 1024)  # stoch_dim = 1024
    
    def _one_hot_from_logits(self, logits: torch.Tensor) -> torch.Tensor:
        """Straight-through Gumbel-softmax one-hot 샘플링."""
        y_soft = torch.softmax(logits, dim=-1)
        index = y_soft.max(-1, keepdim=True)[1]
        y_hard = torch.zeros_like(logits).scatter_(-1, index, 1.0)
        return (y_hard - y_soft).detach() + y_soft

# ============================================================================
# 멀티모달 월드 모델
# ============================================================================

class MultimodalWorldModel(nn.Module):
    """완전한 멀티모달 월드 모델."""
    
    def __init__(self, modality_configs: Dict[str, ModalityConfig]):
        super().__init__()
        self.modality_configs = modality_configs
        self.rssm = MultimodalRSSM(modality_configs)
        
        # 보상 및 연속성 예측기
        latent_dim = 256 + 1024  # deter_dim + stoch_dim
        self.reward_pred = nn.Sequential(
            nn.Linear(latent_dim, 512),
            nn.ELU(),
            nn.Linear(512, 256),
            nn.ELU(),
            nn.Linear(256, 1)
        )
        
        self.continue_pred = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ELU(),
            nn.Linear(256, 1)
        )
    
    def forward(
        self,
        obs_seq: Dict[str, torch.Tensor],
        h_init: Optional[torch.Tensor] = None,
        stoch_init: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """멀티모달 관찰 시퀀스 처리."""
        # 배치 크기와 시퀀스 길이를 임의의 모달리티에서 가져오기
        B = next(iter(obs_seq.values())).size(0)
        T = next(iter(obs_seq.values())).size(1)
        device = next(iter(obs_seq.values())).device
        
        # 상태 초기화
        if h_init is None:
            h_init = torch.zeros(B, 256, device=device)  # deter_dim
        if stoch_init is None:
            stoch_init = torch.zeros(B, 1024, device=device)  # stoch_dim
        
        # 저장소
        embeds, hs, stochs = [], [], []
        post_logits_seq, prior_logits_seq = [], []
        
        h, stoch = h_init, stoch_init
        
        # 시퀀스 처리
        for t in range(T):
            # 시간 t에서 관찰 추출
            obs_t = {k: v[:, t] for k, v in obs_seq.items()}
            
            # RSSM 스텝
            result = self.rssm.dynamics_step(obs_t, h, stoch)
            h = result["h"]
            stoch = result["stoch"]
            
            # 저장
            embeds.append(result["embed"])
            hs.append(h)
            stochs.append(stoch)
            post_logits_seq.append(result["post_logits"])
            prior_logits_seq.append(result["prior_logits"])
        
        # 시퀀스 스택
        hs = torch.stack(hs, dim=1)
        stochs = torch.stack(stochs, dim=1)
        
        # 모든 타임스텝 디코딩
        reconstructions = defaultdict(list)
        for t in range(T):
            recon_t = self.rssm.decode_state(hs[:, t], stochs[:, t])
            for name, recon in recon_t.items():
                reconstructions[name].append(recon)
        
        # 재구성 스택
        for name in reconstructions:
            reconstructions[name] = torch.stack(reconstructions[name], dim=1)
        
        # 보상 및 연속성 예측
        states = torch.cat([hs, stochs], dim=-1)
        states_flat = states.view(-1, states.size(-1))
        
        rewards = self.reward_pred(states_flat).view(B, T)
        continues = torch.sigmoid(self.continue_pred(states_flat)).view(B, T)
        
        return {
            "embeds": torch.stack(embeds, dim=1),
            "hs": hs,
            "stochs": stochs,
            "post_logits": torch.stack(post_logits_seq, dim=1),
            "prior_logits": torch.stack(prior_logits_seq, dim=1),
            "reconstructions": dict(reconstructions),
            "rewards": rewards,
            "continues": continues
        }

# ============================================================================
# 멀티모달 손실
# ============================================================================

class MultimodalLoss(nn.Module):
    """멀티모달 월드 모델용 손실 계산."""
    
    def __init__(self, modality_configs: Dict[str, ModalityConfig]):
        super().__init__()
        self.modality_configs = modality_configs
        
    def forward(
        self,
        obs_true: Dict[str, torch.Tensor],
        reconstructions: Dict[str, torch.Tensor],
        rewards_true: torch.Tensor,
        rewards_pred: torch.Tensor,
        continues_true: torch.Tensor,
        continues_pred: torch.Tensor,
        post_logits: torch.Tensor,
        prior_logits: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """모든 손실 계산."""
        losses = {}
        
        # 각 모달리티의 재구성 손실
        for name, config in self.modality_configs.items():
            if name in obs_true and name in reconstructions:
                if config.loss_type == "mse":
                    loss = F.mse_loss(reconstructions[name], obs_true[name])
                elif config.loss_type == "ce":
                    # 텍스트용: (B, T, L, V) vs (B, T, L)
                    loss = F.cross_entropy(
                        reconstructions[name].transpose(-1, -2),
                        obs_true[name].long()
                    )
                elif config.loss_type == "bce":
                    loss = F.binary_cross_entropy_with_logits(
                        reconstructions[name], obs_true[name]
                    )
                
                losses[f"recon_{name}"] = loss * config.loss_weight
        
        # KL 손실
        B, T = post_logits.shape[:2]
        post_logits_reshaped = post_logits.view(B, T, 32, 32)  # group=32, categ=32
        prior_logits_reshaped = prior_logits.view(B, T, 32, 32)
        
        post_dist = torch.distributions.Categorical(logits=post_logits_reshaped)
        prior_dist = torch.distributions.Categorical(logits=prior_logits_reshaped)
        
        kl = torch.distributions.kl_divergence(post_dist, prior_dist).sum(-1)
        kl = torch.maximum(kl, torch.tensor(3.0))  # Free nats
        losses["kl"] = kl.mean()
        
        # 보상 및 연속성 손실
        def symlog(x: torch.Tensor) -> torch.Tensor:
            return torch.sign(x) * torch.log(torch.abs(x) + 1)
        
        losses["reward"] = F.mse_loss(rewards_pred, symlog(rewards_true))
        losses["continue"] = F.binary_cross_entropy(continues_pred, continues_true.float())
        
        # 총 손실
        losses["total"] = sum(losses.values())
        
        return losses

# ============================================================================
# 사용 예시
# ============================================================================

def create_multimodal_model():
    """멀티모달 Dreamer V3 모델 생성."""
    # 사용할 모달리티 정의
    active_modalities = {
        "image": MODALITY_CONFIGS["image"],
        "text": MODALITY_CONFIGS["text"],
        "vector": MODALITY_CONFIGS["vector"]
    }
    
    # 모델 생성
    model = MultimodalWorldModel(active_modalities)
    return model

def process_multimodal_batch(model: MultimodalWorldModel):
    """멀티모달 데이터 처리 예시."""
    # 더미 배치 생성
    batch_size = 16
    seq_len = 32
    
    obs_seq = {
        "image": torch.randn(batch_size, seq_len, 3, 64, 64),
        "text": torch.randint(0, 30000, (batch_size, seq_len, 100)),
        "text_mask": torch.ones(batch_size, seq_len, 100).bool(),
        "vector": torch.randn(batch_size, seq_len, 779)
    }
    
    # 순전파
    outputs = model(obs_seq)
    
    # 손실 계산
    loss_fn = MultimodalLoss(model.modality_configs)
    
    losses = loss_fn(
        obs_true=obs_seq,
        reconstructions=outputs["reconstructions"],
        rewards_true=torch.randn(batch_size, seq_len),
        rewards_pred=outputs["rewards"],
        continues_true=torch.ones(batch_size, seq_len),
        continues_pred=outputs["continues"],
        post_logits=outputs["post_logits"],
        prior_logits=outputs["prior_logits"]
    )
    
    return outputs, losses

if __name__ == "__main__":
    # 멀티모달 모델 테스트
    model = create_multimodal_model()
    print(f"모델 파라미터: {sum(p.numel() for p in model.parameters()):,}")
    
    # 순전파 테스트
    outputs, losses = process_multimodal_batch(model)
    print("\n손실:")
    for name, loss in losses.items():
        if name != "total":
            print(f"  {name}: {loss.item():.4f}")
    print(f"  총합: {losses['total'].item():.4f}") 