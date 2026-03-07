# 런북

> 이 문서는 Template Engine이 초기 구조를 생성하고,
> Claude가 개발·운영 과정에서 구체적 절차를 채워갑니다.

---

## 1. 배포 개요

| 서비스 | 배포 대상 | CI | CD | 시크릿 관리 |
|--------|----------|-----|-----|-----------|
| sdwc-api | kubernetes | github_actions | argocd | env_file |
| sdwc-web | kubernetes | github_actions | argocd | env_file |

---

## 2. 환경 구성

### sdwc-api

| 환경 | 목적 | 프로덕션과 차이 |
|------|------|---------------|
| dev | Local development and testing | Runs directly via uvicorn, no container |
| production | k3s cluster on Windows WSL2 | Containerized, served behind k3s Traefik ingress |
### sdwc-web

| 환경 | 목적 | 프로덕션과 차이 |
|------|------|---------------|
| dev | Local development with Vite dev server | Hot reload, proxied API requests to local sdwc-api |
| production | Static files served via nginx container in k3s | Built assets served by nginx, API requests routed via k3s ingress |

---

## 3. 배포 절차

<!-- Claude: 첫 배포 성공 후 실제 수행한 명령어/절차 기반으로 작성.
     "이 문서만 보고 배포할 수 있는가?"가 기준.
     배포 환경 변경 시 즉시 갱신. -->

<!--
### [서비스명] 배포

#### 사전 체크리스트
- [ ] ...

#### 배포 명령어
```bash
...
```

#### 검증 단계
1. ...

#### 롤백 절차
1. ...
-->

---

## 4. 롤백 계획

Revert k8s deployment via ArgoCD rollback


---

## 5. 인시던트 대응


---

## 6. 장애 대응 플레이북

<!-- Claude: 인시던트 해결 후, 동일 장애 재발 시 즉시 대응 가능하도록 기록.
     11-troubleshooting은 "왜 발생했나" (원인 분석),
     여기는 "다시 발생하면 어떻게 하나" (대응 절차)에 집중. -->

<!--
### [장애 유형]
- **증상**:
- **진단 순서**:
- **대응 절차**:
- **에스컬레이션**:
-->
