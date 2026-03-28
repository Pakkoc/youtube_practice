> **⚠️ ARCHIVED (2026-03)**: 이 문서에서 제안된 모든 개선안은 이미 구현 완료되었습니다.
> - Bug A: `@requires_profile()` 데코레이터 → `app/cli.py`에 적용됨
> - Bug B: `Project.project_type` computed field → `entities/project/model.py`에 적용됨
> - CLI CC 경고 → `app/cli.py` `pipeline_script_to_shorts`에 적용됨
>
> 이 문서는 히스토리 참조용으로만 유지됩니다.

# Config Race Condition + Skill Routing 구조 개선안

> 2026-03-18 작성 | 새 세션에서 구현 시 이 문서를 컨텍스트로 제공

---

## 1. 문제 요약

### Bug A: CONFIG_PROFILE 싱글턴 레이스 컨디션

**증상**: CC Shorts TTS가 정배속(1.0x)으로 생성됨. shorts 프로필(1.17x)이 적용 안 됨.

**원인 흐름**:
```
cli() group (line 42)
  → get_config()             # CONFIG_PROFILE=base/api로 싱글턴 캐시
  └→ pipeline_script_to_shorts()
       → os.environ["CONFIG_PROFILE"] = "shorts"   # 이미 늦음
       → ctx.obj["config"]                          # 캐시된 base config 반환
```

`get_config()`이 CLI group에서 **eager-load** → 싱글턴 캐시 → subcommand에서 프로필 변경해도 무시됨.

**현재 핫픽스**: `pipeline_script_to_shorts()`에서 `reload_config()` 호출. 동작하지만 근본 해결 아님 — 새 파이프라인 추가 시 같은 실수 반복 가능.

### Bug B: CC 프로젝트에 일반 스킬 사용

**증상**: CC Shorts TSX가 CC 포맷 패턴 없이 생성됨 (일반 쇼츠 레이아웃 적용).

**원인**: `/generate-shorts-slides`(일반 쇼츠)와 `/build-cc-shorts`(CC 전용)가 별도 스킬. AI가 잘못된 스킬을 선택하면 CC 필수 로직(포맷 패턴, 1080x1080 중앙, 아트 디렉션) 전부 누락.

**현재 핫픽스**: `/generate-shorts-slides` 상단에 "cc-XXX이면 STOP" 마크다운 경고. AI가 무시할 수 있어 구조적 보장 없음.

---

## 2. 해결 방안

### Bug A 해결: `@requires_profile` 데코레이터

**핵심 아이디어**: 파이프라인 커맨드가 필요한 프로필을 **선언적으로** 명시. 데코레이터가 config 로딩 타이밍을 관리.

#### Before (현재)
```python
@click.group()
def cli(ctx, config_path, verbose):
    ctx.obj["config"] = get_config(config_path)  # eager-load, 싱글턴 고정

@pipeline.command("script-to-shorts")
def pipeline_script_to_shorts(ctx, ...):
    # 핫픽스: reload_config() 수동 호출
    os.environ["CONFIG_PROFILE"] = "shorts"
    config = reload_config()
```

#### After (개선)
```python
@click.group()
def cli(ctx, config_path, verbose):
    ctx.obj["config_path"] = config_path
    # config 로딩을 subcommand로 위임 (lazy)

@pipeline.command("script-to-shorts")
@requires_profile("shorts")  # ← 선언적
def pipeline_script_to_shorts(ctx, ...):
    config = ctx.obj["config"]  # 데코레이터가 올바른 프로필로 세팅 완료
```

#### `@requires_profile` 데코레이터 동작

```
1. ctx.obj["config_path"] 존재? → 사용자 명시 config 존중 (프로필 변경 안 함)
2. 미존재? → CONFIG_PROFILE 환경변수를 선언된 프로필로 설정
3. 기존 캐시된 config와 프로필 불일치? → reload_config() 호출
4. 프로필 전환 시 경고 메시지 출력
```

#### 구현 위치

- `app/cli.py`에 `requires_profile()` 함수 추가 (~15줄)
- `cli()` group에서 `get_config()` 제거, `config_path`만 저장
- 기존 subcommand들: `@requires_profile("base")` 추가 (또는 프로필 미지정 시 base 기본)
- `pipeline_script_to_shorts`: `@requires_profile("shorts")`

#### 영향 범위

| 파일 | 변경 |
|------|------|
| `app/cli.py` | `requires_profile` 데코레이터 + cli() group 변경 + 각 subcommand 데코레이터 추가 |
| `app/config.py` | 변경 없음 (reload_config 이미 존재) |
| `tests/test_cli.py` | 데코레이터 단위 테스트 추가 |

#### 검증 방법

```bash
# 1. 기존 테스트 통과
uv run pytest tests/test_cli.py -v

# 2. shorts 프로필 강제 적용 확인
uv run video-automation pipeline script-to-shorts --help
# → "[yellow]-> shorts 프로필 자동 적용" 경고 출력

# 3. --config 명시 시 프로필 존중
uv run video-automation --config config/config.api.yaml pipeline script-to-shorts --help
# → 프로필 변경 없음
```

---

### Bug B 해결: `Project.project_type` 계산 필드

**핵심 아이디어**: 프로젝트 이름에서 타입을 자동 분류. 코드 레벨에서 분기 가능.

#### 구현

```python
# entities/project/model.py
class Project(BaseModel):
    name: str

    @computed_field
    @property
    def project_type(self) -> Literal["standard", "cc"]:
        """프로젝트 이름 패턴으로 타입 분류."""
        return "cc" if re.match(r"cc-\d+", self.name) else "standard"
```

#### 활용처

1. **파이프라인 코드** — CC 프로젝트일 때 자동 동작 조정:
```python
# pipelines/script_to_shorts/lib.py
if project.project_type == "cc":
    logger.info("CC 프로젝트 감지: CC 전용 설정 적용")
```

2. **스킬 마크다운** — 현재 텍스트 경고 유지 (보조 수단):
```markdown
## CC Shorts Project Detection
프로젝트 이름이 cc-XXX 패턴이면 STOP. /build-cc-shorts 사용.
```

3. **CLI 출력** — 어떤 스킬을 써야 하는지 안내:
```python
# app/cli.py pipeline_script_to_shorts()
if project.project_type == "cc":
    console.print("[yellow]CC 프로젝트입니다. TSX 생성은 /build-cc-shorts를 사용하세요.[/yellow]")
```

#### 영향 범위

| 파일 | 변경 |
|------|------|
| `entities/project/model.py` | `project_type` computed field 추가 |
| `app/cli.py` | CC 프로젝트 안내 메시지 추가 (선택) |
| `tests/entities/test_project.py` | project_type 단위 테스트 |

#### 검증 방법

```python
# 단위 테스트
def test_project_type_cc():
    assert Project(name="cc-001").project_type == "cc"
    assert Project(name="cc-035").project_type == "cc"

def test_project_type_standard():
    assert Project(name="my-video").project_type == "standard"
    assert Project(name="cc-intro").project_type == "standard"  # 숫자 아님
```

---

## 3. 구현 순서

```
Step 1: @requires_profile 데코레이터 구현 + cli() group 변경
Step 2: 기존 subcommand에 데코레이터 적용
Step 3: Project.project_type 추가
Step 4: CLI에 CC 프로젝트 안내 메시지 추가
Step 5: 테스트 작성 + 전체 테스트 통과 확인
Step 6: 기존 핫픽스 코드 정리 (reload_config 수동 호출 제거)
```

---

## 4. 판단 포인트

이 문서를 새 세션에 넘길 때, 아래 사항만 결정하면 바로 구현 가능:

- [ ] **Bug A**: `@requires_profile` 방식으로 진행할지, 다른 방식 선호하는지
- [ ] **Bug B**: `Project.project_type` 외에 스킬 통합(/build-shorts 단일 진입점)도 검토할지
- [ ] **범위**: A+B 동시 진행 vs 하나씩 순차 진행
