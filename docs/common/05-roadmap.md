# 로드맵

---

## 1. 향후 기능

| 기능 | 예정 시점 | 아키텍처 영향 | 지금 준비할 것 |
|------|----------|-------------|-------------|
| Selective regeneration (service-level scope) | v2 | Template Engine needs scope parameter, output_contract needs per-scope validation | .sdwc/ server resources included in ZIP enables Claude-driven updates without SDwC |
| New framework additions | post_launch | No architecture change -- add skill-templates folder only | Coding-standards common skeleton (S1~S7) already established |

---

## 3. 기술 리스크

| 리스크 | 가능성 | 영향 | 완화 방안 | Plan B |
|--------|--------|------|----------|--------|
| Template rendering performance degrades with complex intake data | low | medium | Set 10s response time target for /generate, monitor via structured logs | Profile and optimize hot paths in Template Engine |
| k3s on WSL2 has stability issues | medium | low | Not a production-critical service, acceptable for practice environment | Fall back to Docker Compose if k3s is unstable |

---

## 4. 되돌리기 어려운 결정

| 결정 | 왜 되돌리기 어려운가 | 확신도 | 되돌림 비용 |
|------|-------------------|--------|-----------|
| Handlebars -> Jinja2 template migration | 160 template files rewritten. Reverting means re-converting all files | high | High -- full re-conversion of 160 files |
| Python/FastAPI as backend language/framework | All server code, Template Engine, and validation logic in Python | high | Full rewrite |

---


## 6. 롤아웃 계획

- **전략**: big_bang


- **롤백 계획**: Revert k8s deployment via ArgoCD rollback

---

## 7. 운영 계획

- **문서 관리**: Claude maintains docs per CLAUDE.md S6 rules. .sdwc/ resources enable self-sufficient project evolution

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
