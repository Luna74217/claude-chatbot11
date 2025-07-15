# Dreamer V3 + Hierarchical PPO + Curiosity/Empowerment/Meta-gradient

이 프로젝트는 Dreamer V3와 Hierarchical PPO, 그리고 Curiosity/Empowerment/Meta-gradient를 결합한 고급 강화학습 시스템입니다.

## 🚀 주요 특징

### Core Components
- **Dreamer V3**: 세계 모델 기반 강화학습
- **Hierarchical PPO**: 계층적 정책 최적화
- **Intrinsic Motivation**: 
  - ICM (Intrinsic Curiosity Module)
  - Empowerment (Variational Empowerment)
- **Meta-gradient Optimization**: 학습률 자동 조정

### Multimodal Support
- **이미지**: CNN 기반 인코더/디코더
- **텍스트**: Transformer 기반 처리
- **오디오**: 1D CNN 처리
- **벡터**: MLP 기반 처리

## 📁 프로젝트 구조

```
dreamer-v3-system/
├── dreamer_v3_improved.py      # 개선된 메인 시스템
├── dreamer_v3_multimodal.py    # 멀티모달 확장
├── run_dreamer.py              # 실행 스크립트
├── configs/
│   └── default.json            # 기본 설정
├── checkpoints/                # 체크포인트 저장
└── README_DREAMER.md          # 이 파일
```

## 🛠️ 설치

### 필수 의존성

```bash
pip install torch torchvision torchaudio
pip install numpy
pip install wandb  # 실험 추적용
pip install gym    # 환경용
pip install einops # 텐서 조작용
```

### 선택적 의존성

```bash
pip install transformers  # 텍스트 처리용
pip install librosa       # 오디오 처리용
pip install pillow        # 이미지 처리용
```

## 🎯 사용법

### 기본 실행

```bash
# 기본 설정으로 훈련
python run_dreamer.py

# 커스텀 설정으로 훈련
python run_dreamer.py --config configs/custom.json

# 멀티모달 모델로 훈련
python run_dreamer.py --multimodal

# 체크포인트에서 재시작
python run_dreamer.py --checkpoint checkpoints/best_model.pt

# GPU 사용
python run_dreamer.py --device cuda

# 훈련 스텝 수 조정
python run_dreamer.py --steps 500000
```

### 설정 파일 예시

```json
{
    "obs_dim": 779,
    "embed_dim": 1024,
    "action_dim": 5,
    "batch_size": 16,
    "seq_len": 64,
    "world_lr": 0.0006,
    "actor_lr": 0.0003,
    "use_wandb": true
}
```

## 🔧 주요 컴포넌트

### 1. DreamerV3Trainer

메인 훈련 클래스로 다음 기능을 제공합니다:

- **에피소드 수집**: 현재 정책으로 환경과 상호작용
- **월드 모델 훈련**: 관찰 재구성 및 예측
- **정책 훈련**: PPO를 통한 계층적 정책 최적화
- **내재적 보상**: Curiosity와 Empowerment 훈련
- **메타 그래디언트**: 학습률 자동 조정

### 2. SequenceReplayBuffer

시퀀스 기반 리플레이 버퍼:

- 오버래핑 시퀀스 생성
- 배치 샘플링
- 버퍼 통계 모니터링

### 3. MultimodalWorldModel

멀티모달 관찰 지원:

- 이미지, 텍스트, 오디오, 벡터 처리
- 모달리티별 인코더/디코더
- 교차 모달리티 어텐션

## 📊 모니터링

### Wandb 통합

```python
# 자동으로 다음 메트릭을 추적합니다:
- episode/return: 에피소드 보상
- episode/length: 에피소드 길이
- world/recon_loss: 재구성 손실
- world/kl_loss: KL 발산 손실
- policy/policy_loss: 정책 손실
- intrinsic/icm_loss: Curiosity 손실
- meta/lr: 적응적 학습률
```

### 로깅

```bash
# 로그 레벨 조정
python run_dreamer.py --log-level DEBUG

# 콘솔 출력 예시:
INFO - Step 1000: {'world/recon_loss': 0.1234, 'policy/policy_loss': 0.5678}
INFO - Episode return: 150.5, length: 200
```

## 🔬 실험 설정

### 하이퍼파라미터 튜닝

```python
# configs/experiment.json
{
    "kl_scale": [0.5, 1.0, 2.0],
    "free_nats": [1.0, 3.0, 5.0],
    "clip_ratio": [0.1, 0.2, 0.3]
}
```

### 멀티모달 실험

```python
# 이미지 + 텍스트 조합
active_modalities = {
    "image": MODALITY_CONFIGS["image"],
    "text": MODALITY_CONFIGS["text"]
}

# 모든 모달리티 사용
active_modalities = MODALITY_CONFIGS
```

## 🐛 문제 해결

### 일반적인 문제

1. **CUDA 메모리 부족**
   ```bash
   # 배치 크기 줄이기
   python run_dreamer.py --config configs/small_batch.json
   ```

2. **훈련 불안정**
   ```bash
   # 그래디언트 클리핑 조정
   # 학습률 감소
   # Free nats 증가
   ```

3. **환경 오류**
   ```bash
   # 환경 재설치
   pip install --upgrade gym
   ```

### 디버깅

```bash
# 상세 로깅
python run_dreamer.py --log-level DEBUG

# 체크포인트 검사
python -c "
import torch
checkpoint = torch.load('checkpoints/best_model.pt')
print(checkpoint.keys())
"
```

## 📈 성능 최적화

### 메모리 최적화

- **그래디언트 체크포인팅**: 긴 시퀀스 처리
- **혼합 정밀도**: FP16 훈련
- **배치 크기 조정**: 메모리 사용량에 따라

### 속도 최적화

- **멀티프로세싱**: 환경 병렬화
- **JIT 컴파일**: 모델 최적화
- **데이터 로딩**: 비동기 데이터 로딩

## 🔄 확장성

### 새로운 모달리티 추가

```python
# 1. 모달리티 설정 정의
new_modality = ModalityConfig(
    name="new_type",
    input_shape=(dim1, dim2),
    embed_dim=256,
    encoder_type="custom",
    decoder_type="custom"
)

# 2. 인코더/디코더 구현
class CustomEncoder(nn.Module):
    def forward(self, x):
        # 구현
        pass

# 3. 모델에 추가
MODALITY_CONFIGS["new_type"] = new_modality
```

### 새로운 환경 추가

```python
def create_custom_env():
    # 커스텀 환경 구현
    return CustomEnvironment()

# 실행 시 사용
python run_dreamer.py --env custom
```

## 📚 참고 자료

- [Dreamer V3 Paper](https://arxiv.org/abs/2301.04104)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [ICM Paper](https://arxiv.org/abs/1705.05363)
- [Empowerment Paper](https://arxiv.org/abs/1810.03343)

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 라이선스

MIT License

## 📞 문의

문제나 질문이 있으시면 이슈를 생성해주세요. 