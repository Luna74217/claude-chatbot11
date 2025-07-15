#!/usr/bin/env python3
"""
Dreamer V3 파일 호환성 검사 (Slim)
"""
import sys, json, importlib
from pathlib import Path

class CompatibilityChecker:
    def __init__(self):
        self.errors, self.warnings, self.success = [], [], []
    def log_error(self, msg): self.errors.append(msg); print(f"[ERROR] {msg}")
    def log_success(self, msg): self.success.append(msg)
    def check_file_exists(self, filepath):
        if Path(filepath).exists(): self.log_success(f"파일 존재: {filepath}"); return True
        self.log_error(f"파일 없음: {filepath}"); return False
    def check_imports(self, module_name):
        try: importlib.import_module(module_name); self.log_success(f"Import: {module_name}"); return True
        except Exception as e: self.log_error(f"Import 실패: {module_name} - {e}"); return False
    def check_json_syntax(self, filepath):
        try: json.load(open(filepath, encoding='utf-8')); self.log_success(f"JSON OK: {filepath}"); return True
        except Exception as e: self.log_error(f"JSON 오류: {filepath} - {e}"); return False
    def check_config_compatibility(self):
        path = "configs/default.json"
        if not self.check_file_exists(path): return False
        if not self.check_json_syntax(path): return False
        try:
            from dreamer_v3_improved import DreamerConfig
            config = DreamerConfig(**json.load(open(path, encoding='utf-8')))
            assert config.stoch_dim == config.categ * config.group
            self.log_success("설정 객체 생성 OK")
            return True
        except Exception as e: self.log_error(f"설정 호환성 실패: {e}"); return False
    def check_model_compatibility(self):
        try:
            from dreamer_v3_improved import DreamerConfig, DreamerV3Trainer
            from dreamer_v3_multimodal import MultimodalWorldModel, create_multimodal_model
            model = create_multimodal_model(); p = sum(p.numel() for p in model.parameters())
            self.log_success(f"모델 파라미터: {p}"); return True
        except Exception as e: self.log_error(f"모델 호환성 실패: {e}"); return False
    def check_dependencies(self):
        pkgs = ['torch','numpy','wandb','einops','gym']
        ok = True
        for p in pkgs:
            if not self.check_imports(p): ok = False
        return ok
    def check_file_structure(self):
        files = ['dreamer_v3_improved.py','dreamer_v3_multimodal.py','run_dreamer.py','configs/default.json','requirements_dreamer.txt','README_DREAMER.md']
        return all(self.check_file_exists(f) for f in files)
    def check_code_syntax(self):
        files = ['dreamer_v3_improved.py','dreamer_v3_multimodal.py','run_dreamer.py']
        ok = True
        for f in files:
            try: compile(open(f,encoding='utf-8').read(), f, 'exec'); self.log_success(f"문법 OK: {f}")
            except Exception as e: self.log_error(f"문법 오류: {f} - {e}"); ok = False
        return ok
    def run_all_checks(self):
        print("[호환성 검사 시작]")
        checks = {
            "파일 구조": self.check_file_structure(),
            "코드 문법": self.check_code_syntax(),
            "의존성": self.check_dependencies(),
            "설정": self.check_config_compatibility(),
            "모델": self.check_model_compatibility()
        }
        print("[결과 요약]")
        for k,v in checks.items(): print(f"{k}: {'OK' if v else 'FAIL'}")
        print(f"총 통과: {sum(checks.values())}/{len(checks)}")
        if self.errors: print("오류:", *self.errors, sep='\n- ')
        return checks

def main():
    checker = CompatibilityChecker()
    checker.run_all_checks()
    sys.exit(0)

if __name__ == "__main__":
    main() 