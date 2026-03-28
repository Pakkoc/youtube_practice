# 워크숍 배포용 zip 빌드 가이드

> 강의 전/후에 수강생에게 배포할 zip을 만드는 절차.

---

## 포함/제외 기준

### 포함

| 대상 | 이유 |
|------|------|
| `app/`, `pipelines/`, `features/`, `entities/`, `shared/` | 핵심 소스코드 |
| `.claude/` (commands, rules, agents, hooks, skills) | 스킬/커맨드/룰 (Claude Code 필수) |
| `.agents/` | 에이전트 스킬 |
| `remotion/src/` + `remotion/docs/` | TSX 슬라이드 + 패턴 레퍼런스 |
| `remotion/package.json`, `tsconfig.json`, `remotion.config.ts` | npm install에 필요 |
| `prompts/`, `tests/` | LLM 프롬프트 + 테스트 |
| `config/config.api.yaml`, `config/tts_dictionary.yaml` | API-only 설정 |
| `workshop/`, `docs/` | 교육 자료 |
| `assets/fonts/Pretendard-{Regular,Bold,SemiBold}.otf` | 핵심 폰트 3개만 |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python 빌드 |
| `.env.example`, `.gitignore`, `CLAUDE.md`, `install-guideline.md`, `README.md`, `LICENSE` | 루트 필수 파일 |
| `projects/.gitkeep` | 빈 디렉토리 유지 |

### 제외

| 대상 | 이유 |
|------|------|
| `projects/` 내 데이터 | 개인 영상 프로젝트 (2GB+) |
| `remotion/node_modules/` | `npm install`로 재생성 (400MB+) |
| `.venv/`, `__pycache__/`, `*.pyc` | 빌드 아티팩트 |
| `.env` | API 키 (비밀정보) |
| `.claude/settings.local.json` | 개인 Claude Code 설정 |
| `config/config.base.yaml`, `config.asmr.yaml`, `config.shorts.yaml` | GPU 전용 프로필 |
| `voice-fine-tuning/` | 음성 클론 모델 (GPU 전용) |
| `assets/fonts/alternative/` | 대체 폰트 (23MB) |
| `assets/references/`, `assets/avatar_image/` | 개인 에셋 |
| `.git/` | git 히스토리 |
| `youtube-automation-workshop.zip` | 이전 빌드 결과물 |

---

## zip 안에서 변경되는 파일 (원본과 다름)

| 파일 | 변경 내용 |
|------|----------|
| `app/config.py` | `DEFAULT_PROFILE = "base"` → `"api"` |
| `CLAUDE.md` | API-only 워크숍 버전 (GPU/B-roll/아바타 제거) |
| `config/` | `config.api.yaml`만 포함 (base/asmr/shorts 제거) |
| `install-guideline.md` | `CONFIG_PROFILE=api` 접두어 제거 |
| `workshop/*.md`, `docs/*.md` | `CONFIG_PROFILE=api` 접두어 제거 |

---

## 빌드 명령어

프로젝트 루트에서 실행:

```bash
cd /Volumes/External_SSD\(hotorch\)/DEVELOPMENT/samhottman-youtube-automation-factory

BUILDDIR="$(pwd)/_build_workshop"
rm -rf "$BUILDDIR"
W="$BUILDDIR/youtube-automation-workshop"
mkdir -p "$W"

# 1. 소스코드 복사
for dir in app pipelines features entities shared prompts tests; do
  rsync -a --exclude='__pycache__' --exclude='*.pyc' "$dir/" "$W/$dir/"
done

# 2. DEFAULT_PROFILE → "api"
sed -i '' 's/DEFAULT_PROFILE = "base"/DEFAULT_PROFILE = "api"/' "$W/app/config.py"

# 3. .claude + .agents (개인 설정 제외)
rsync -a --exclude='__pycache__' --exclude='settings.local.json' .claude/ "$W/.claude/"
rsync -a --exclude='__pycache__' .agents/ "$W/.agents/"

# 4. Remotion (src + docs + 설정파일, node_modules 제외)
mkdir -p "$W/remotion"
rsync -a --exclude='node_modules' --exclude='.cache' --exclude='__pycache__' remotion/src/ "$W/remotion/src/"
rsync -a remotion/docs/ "$W/remotion/docs/"
cp remotion/package.json remotion/tsconfig.json remotion/remotion.config.ts "$W/remotion/"

# 5. 폰트 (핵심 3개만)
mkdir -p "$W/assets/fonts"
cp assets/fonts/Pretendard-{Regular,Bold,SemiBold}.otf "$W/assets/fonts/"

# 6. 문서
rsync -a workshop/ "$W/workshop/" 2>/dev/null || true
rsync -a docs/ "$W/docs/" 2>/dev/null || true

# 7. 루트 파일
cp pyproject.toml README.md .env.example .gitignore install-guideline.md "$W/"
cp .python-version uv.lock "$W/" 2>/dev/null || true

# 8. config (API only)
mkdir -p "$W/config"
cp config/tts_dictionary.yaml "$W/config/"
cp config/config.api.yaml "$W/config/"

# 9. Workshop CLAUDE.md (아래 별도 섹션 참고)
# → 기존 CLAUDE.md 대신 워크숍 버전으로 교체
# → 내용은 "워크숍 CLAUDE.md 원문" 섹션 참고

# 10. LICENSE
# → 내용은 "LICENSE 원문" 섹션 참고

# 11. projects 빈 디렉토리
mkdir -p "$W/projects" && touch "$W/projects/.gitkeep"

# 12. 문서에서 접두어 제거
sed -i '' 's///g' "$W/install-guideline.md"
sed -i '' 's/CONFIG_PROFILE=community //g' "$W/install-guideline.md"
find "$W/workshop" -name "*.md" -exec sed -i '' 's///g' {} +
find "$W/docs" -name "*.md" -exec sed -i '' 's///g' {} +

# 13. zip 생성
OUTPUT="$(pwd)/youtube-automation-workshop.zip"
rm -f "$OUTPUT"
cd "$BUILDDIR" && zip -r "$OUTPUT" youtube-automation-workshop -x "*.DS_Store" "*__pycache__*" > /dev/null

# 14. 정리
rm -rf "$BUILDDIR"

echo "완료: $(ls -lh "$OUTPUT" | awk '{print $5}') $OUTPUT"
```

---

## 빌드 후 검증

```bash
# 핵심 파일 존재 확인
unzip -l youtube-automation-workshop.zip | grep -E "(CLAUDE\.md|LICENSE|config\.api|install-guideline|\.env\.example)"

# .claude + .agents 포함 확인
unzip -l youtube-automation-workshop.zip | grep -cE "\.(claude|agents)/"

# DEFAULT_PROFILE 확인 (임시 압축 해제)
unzip -p youtube-automation-workshop.zip youtube-automation-workshop/app/config.py | grep DEFAULT_PROFILE

# 잔여 확인 (0이어야 함)
unzip -p youtube-automation-workshop.zip youtube-automation-workshop/install-guideline.md | grep -c "CONFIG_PROFILE=api"
```

---

## 수강생 사용 플로우

```
1. zip 다운로드 → 바탕화면에 압축 해제
2. cd youtube-automation-workshop
3. cd remotion && npm install && cd ..
4. uv sync --extra genai && uv sync --extra dev
5. cp .env.example .env → API 키 입력
6. claude --dangerously-skip-permissions
7. /generate-video my-video   ← CONFIG_PROFILE 불필요
```
