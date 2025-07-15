#!/usr/bin/env python3
"""
Dreamer V3 실행 스크립트 (Slim)
"""
import argparse, json, sys
from pathlib import Path
from dreamer_v3_improved import DreamerConfig, DreamerV3Trainer
from dreamer_v3_multimodal import create_multimodal_model, MultimodalWorldModel

def create_env():
    import gym
    return gym.make("CartPole-v1")

def load_config(config_path: str) -> DreamerConfig:
    with open(config_path) as f:
        config_dict = json.load(f)
    return DreamerConfig(**config_dict)

def create_model(config: DreamerConfig, multimodal: bool = False):
    if multimodal:
        from dreamer_v3_multimodal import MODALITY_CONFIGS
        active_modalities = {
            "image": MODALITY_CONFIGS["image"],
            "text": MODALITY_CONFIGS["text"],
            "vector": MODALITY_CONFIGS["vector"]
        }
        return MultimodalWorldModel(active_modalities)
    else:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/default.json")
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=1_000_000)
    parser.add_argument("--multimodal", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.device != "auto":
        config.device = args.device
    import torch, numpy as np
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model = create_model(config, args.multimodal)
    if model is None:
        print("모델 생성 실패"); sys.exit(1)
    if args.checkpoint:
        import torch
        checkpoint = torch.load(args.checkpoint, map_location=config.device)
        model.load_state_dict(checkpoint["model_state"])
    trainer = DreamerV3Trainer(model=model, env_fn=create_env, config=config)
    trainer.train(num_steps=args.steps)

if __name__ == "__main__":
    main() 