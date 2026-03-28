"""Click 기반 CLI 진입점."""

from __future__ import annotations

import functools
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.panel import Panel

from app.config import get_config, reload_config
from app.providers import get_tts_backend_name
from shared.lib.logger import setup_logger
from shared.lib.platform import detect_platform

if TYPE_CHECKING:
    from entities.subtitle.model import SubtitleTrack

console = Console()


def requires_profile(default_profile: str):
    """파이프라인 커맨드에 필요한 config 프로필을 선언적으로 지정.

    사용자가 CONFIG_PROFILE 환경변수를 명시적으로 설정한 경우 그 값을 존중.
    설정하지 않은 경우 default_profile을 사용.
    """

    def decorator(f):
        @functools.wraps(f)
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            if ctx.obj.get("config_path"):
                config = ctx.obj["config"]
            else:
                user_profile = os.getenv("CONFIG_PROFILE")
                if user_profile:
                    profile = user_profile
                    if user_profile != default_profile:
                        console.print(
                            f"[yellow]CONFIG_PROFILE={user_profile}"
                            f" 사용자 지정 프로필 적용"
                            f" (기본: {default_profile})[/yellow]"
                        )
                else:
                    profile = default_profile
                os.environ["CONFIG_PROFILE"] = profile
                config = reload_config()
            ctx.obj["config"] = config
            # ctx.invoke(f) 사용 금지: f에 @click.pass_context가 없어 ctx 누락됨
            return f(ctx, *args, **kwargs)

        return wrapper

    return decorator


@click.group()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="설정 파일 경로 (기본: config/config.yaml)",
)
@click.option("--verbose", "-v", is_flag=True, help="상세 로그 출력")
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None, verbose: bool) -> None:
    """AI 영상 자동화 시스템 - 스크립트에서 유튜브 영상까지."""
    import logging

    ctx.ensure_object(dict)
    level = logging.DEBUG if verbose else logging.INFO
    setup_logger(level=level)
    ctx.obj["config_path"] = config_path
    # config 로딩을 subcommand의 @requires_profile로 위임 (lazy)
    if config_path:
        ctx.obj["config"] = get_config(config_path)


@cli.command()
def info() -> None:
    """현재 환경 정보를 표시합니다."""
    from shared.lib.ffmpeg import check_ffmpeg

    config = get_config()
    platform = detect_platform()
    backend = get_tts_backend_name(config.tts, platform)

    lines = [
        f"[bold]플랫폼:[/bold] {platform.summary}",
        f"[bold]TTS 백엔드:[/bold] {backend}",
        f"[bold]TTS 화자:[/bold] {config.tts.speaker}",
        f"[bold]TTS 언어:[/bold] {config.tts.language}",
        f"[bold]TTS 모델:[/bold] {config.tts.model}",
        f"[bold]FFmpeg:[/bold] {'설치됨' if check_ffmpeg() else '[red]미설치[/red]'}",
    ]

    console.print(Panel("\n".join(lines), title="Video Automation - 환경 정보"))


@cli.group()
def pipeline() -> None:
    """파이프라인 실행."""
    pass


@pipeline.command("script-to-video")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@click.option("--no-broll", "no_broll", is_flag=True, help="B-roll 생성 건너뛰기 (빠른 테스트용)")
@requires_profile("base")
def pipeline_script_to_video(
    ctx: click.Context, input_path: Path, project_name: str, no_broll: bool
) -> None:
    """대본에서 영상을 생성합니다 (슬라이드 + TTS 병렬, B-roll 통합)."""
    from entities.project.model import Project
    from pipelines.script_to_video import run_script_to_video

    config = ctx.obj["config"]

    # 프로젝트 생성 및 대본 복사
    project = Project(name=project_name)
    project.ensure_dirs()

    # 입력 대본을 프로젝트 디렉토리로 복사
    if input_path.resolve() != project.script_path.resolve():
        shutil.copy2(input_path, project.script_path)

    broll_status = "[red]OFF[/red]" if no_broll else "[green]ON[/green]"
    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]입력:[/bold] {input_path}\n"
            f"[bold]출력:[/bold] {project.output_dir}\n"
            f"[bold]B-roll:[/bold] {broll_status}",
            title="Script → Video 파이프라인 (병렬화)",
        )
    )

    try:
        video = run_script_to_video(
            project=project,
            config=config,
            include_broll=not no_broll,
        )
        console.print(
            f"\n[bold green]완료![/bold green] 영상: {video.file_path} ({video.duration:.1f}초)"
        )
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@cli.group()
def tts() -> None:
    """TTS 관련 명령어."""
    pass


@tts.command("generate")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--speaker", default=None, help="TTS 화자 (기본: config 값)")
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.pass_context
def tts_generate(
    ctx: click.Context, input_path: Path, speaker: str | None, output_path: Path | None
) -> None:
    """텍스트에서 TTS 음성을 생성합니다."""
    from features.generate_tts import create_tts_backend, generate_tts_for_text
    from shared.lib.file_io import read_text

    config = ctx.obj.get("config") or get_config()

    if speaker:
        config.tts.speaker = speaker

    text = read_text(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".wav")

    console.print(
        f"[bold green]TTS 생성:[/bold green] {input_path.name} → {output_path.name} "
        f"(화자: {config.tts.speaker})"
    )

    try:
        backend = create_tts_backend(config.tts)
        result = generate_tts_for_text(
            text=text,
            output_path=output_path,
            config=config.tts,
            backend=backend,
        )

        if result.success:
            console.print(
                f"[bold green]완료![/bold green] {result.output_path} ({result.duration:.1f}초)"
            )
        else:
            console.print(f"[bold red]실패:[/bold red] {result.error}")
            raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@tts.command("validate")
@click.option("--audio", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--text", "text_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.pass_context
def tts_validate(ctx: click.Context, audio: Path, text_path: Path) -> None:
    """TTS 오디오 품질을 검증합니다."""
    from features.validate_tts import validate_tts
    from shared.lib.file_io import read_text

    config = ctx.obj.get("config") or get_config()
    original_text = read_text(text_path)

    console.print(f"[bold green]TTS 검증:[/bold green] {audio.name}")

    result = validate_tts(
        audio_path=audio,
        original_text=original_text,
        config=config.validation,
    )

    status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
    console.print(f"결과: {status} (일치율: {result.match_rate:.1%})")
    console.print(f"원본: {result.original[:100]}...")
    console.print(f"STT:  {result.transcribed[:100]}...")


@cli.group()
def subtitles() -> None:
    """자막 관련 명령어."""
    pass


@subtitles.command("add")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@click.pass_context
def subtitles_add(ctx: click.Context, input_path: Path, project_name: str) -> None:
    """영상에 자막과 B-roll을 추가합니다."""
    from entities.project.model import Project
    from pipelines.add_subtitles import run_add_subtitles

    config = ctx.obj.get("config") or get_config()
    project = Project(name=project_name)
    project.ensure_dirs()

    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]입력 영상:[/bold] {input_path}\n"
            f"[bold]출력:[/bold] {project.output_dir}",
            title="자막 + B-roll 파이프라인",
        )
    )

    try:
        output = run_add_subtitles(
            project=project,
            config=config,
            video_path=input_path,
        )
        console.print(f"\n[bold green]완료![/bold green] 영상: {output}")
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@subtitles.command("transcribe")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--language", default="ko", help="언어 코드 (기본: ko)")
def subtitles_transcribe(input_path: Path, output_path: Path | None, language: str) -> None:
    """오디오/영상에서 자막을 추출합니다 (Whisper STT)."""
    from features.transcribe_audio import transcribe_and_save_srt

    if output_path is None:
        output_path = input_path.with_suffix(".srt")

    console.print(f"[bold green]STT 전사:[/bold green] {input_path.name} → {output_path.name}")

    try:
        track = transcribe_and_save_srt(input_path, output_path, language=language)
        console.print(
            f"[bold green]완료![/bold green] {len(track.segments)}개 세그먼트 → {output_path}"
        )
    except Exception as e:
        console.print(f"[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@subtitles.command("correct")
@click.option("--srt", "srt_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--script", "script_path", required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
def subtitles_correct(srt_path: Path, script_path: Path, output_path: Path | None) -> None:
    """STT 자막을 원본 대본과 비교하여 교정합니다."""
    from features.correct_subtitles import correct_and_save_srt
    from shared.lib.file_io import read_text

    if output_path is None:
        output_path = srt_path.with_stem(srt_path.stem + "_corrected")

    console.print(f"[bold green]자막 교정:[/bold green] {srt_path.name}")

    try:
        # SRT → SubtitleTrack 파싱
        track = _parse_srt_file(srt_path)
        original_script = read_text(script_path)

        corrected_track, result = correct_and_save_srt(
            track, original_script, output_path,
        )
        console.print(
            f"[bold green]완료![/bold green] {result.changes_made}개 수정 → {output_path}"
        )
    except Exception as e:
        console.print(f"[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@subtitles.command("burn")
@click.option("--video", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--srt", "srt_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.pass_context
def subtitles_burn(
    ctx: click.Context, video: Path, srt_path: Path,
    output_path: Path | None,
) -> None:
    """영상에 자막을 하드코딩합니다."""
    from features.burn_subtitles import burn_subtitles

    config = ctx.obj.get("config") or get_config()

    if output_path is None:
        output_path = video.with_stem(video.stem + "_subtitled")

    console.print(
        f"[bold green]자막 합성:[/bold green] {video.name} + {srt_path.name}"
    )

    try:
        result = burn_subtitles(video, srt_path, output_path, config=config.subtitles)
        console.print(f"[bold green]완료![/bold green] {result}")
    except Exception as e:
        console.print(f"[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@pipeline.command("video-to-shorts")
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="소스 영상 경로 (미지정 시 자동 탐색)",
)
@click.option("--max-shorts", type=int, default=None, help="최대 쇼츠 수 오버라이드")
@click.option("--max-duration", type=int, default=None, help="최대 길이(초) 오버라이드")
@requires_profile("base")
def pipeline_video_to_shorts(
    ctx: click.Context,
    project_name: str,
    input_path: Path | None,
    max_shorts: int | None,
    max_duration: int | None,
) -> None:
    """기존 영상에서 쇼츠/릴스를 생성합니다."""
    from entities.project.model import Project
    from pipelines.video_to_shorts import run_video_to_shorts

    config = ctx.obj["config"]

    if max_duration is not None:
        config.shorts = config.shorts.model_copy(
            update={"max_duration": max_duration}
        )

    project = Project(name=project_name)
    project.ensure_dirs()

    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]소스:[/bold] {input_path or '자동 탐색'}\n"
            f"[bold]최대 쇼츠:[/bold] {max_shorts or config.shorts.max_shorts}\n"
            f"[bold]길이:[/bold] {config.shorts.min_duration}~{config.shorts.max_duration}초",
            title="Video -> Shorts/Reels 파이프라인",
        )
    )

    try:
        videos = run_video_to_shorts(
            project=project,
            config=config,
            video_path=input_path,
            max_shorts=max_shorts,
        )
        for v in videos:
            console.print(
                f"  [green]>[/green] {v.file_path.name} ({v.duration:.1f}초, {v.width}x{v.height})"
            )
        console.print(
            f"\n[bold green]완료![/bold green] {len(videos)}개 쇼츠 생성 -> {project.shorts_dir}"
        )
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@pipeline.command("script-to-shorts")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@click.option("--no-broll", "no_broll", is_flag=True, help="B-roll 배경 건너뛰기")
@requires_profile("shorts")
def pipeline_script_to_shorts(
    ctx: click.Context, input_path: Path, project_name: str, no_broll: bool
) -> None:
    """대본에서 9:16 쇼츠를 생성합니다 (TSX 슬라이드 + TTS + 워드 자막)."""
    from entities.project.model import Project
    from pipelines.script_to_shorts import run_script_to_shorts

    config = ctx.obj["config"]

    project = Project(name=project_name)
    project.ensure_dirs()

    if project.project_type == "cc":
        console.print(
            "[yellow]CC 프로젝트입니다."
            " TSX 생성은 /build-cc-shorts를 사용하세요.[/yellow]"
        )

    if input_path.resolve() != project.script_path.resolve():
        shutil.copy2(input_path, project.script_path)

    profile_name = os.getenv("CONFIG_PROFILE", "shorts")
    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]입력:[/bold] {input_path}\n"
            f"[bold]출력:[/bold] {project.shorts_slides_dir / 'output'}\n"
            f"[bold]포맷:[/bold] 1080x1920 (9:16)\n"
            f"[bold]프로필:[/bold] {profile_name}",
            title="Script → Shorts 파이프라인",
        )
    )

    try:
        video = run_script_to_shorts(
            project=project,
            config=config,
            include_broll=not no_broll,
        )
        console.print(
            f"\n[bold green]완료![/bold green] 쇼츠: {video.file_path} ({video.duration:.1f}초)"
        )
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@pipeline.command("script-to-carousel")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@requires_profile("base")
def pipeline_script_to_carousel(
    ctx: click.Context, input_path: Path, project_name: str
) -> None:
    """대본에서 인스타그램 카드뉴스(카루셀)를 생성합니다."""
    from entities.project.model import Project
    from pipelines.script_to_carousel import run_script_to_carousel

    config = ctx.obj["config"]

    project = Project(name=project_name)
    project.ensure_dirs()

    # 입력 대본을 프로젝트 디렉토리로 복사
    if input_path.resolve() != project.script_path.resolve():
        shutil.copy2(input_path, project.script_path)

    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]입력:[/bold] {input_path}\n"
            f"[bold]출력:[/bold] {project.carousel_dir}\n"
            f"[bold]최대 카드:[/bold] {config.carousel.max_cards}",
            title="Script -> Carousel 카드뉴스 파이프라인",
        )
    )

    try:
        cards = run_script_to_carousel(project=project, config=config)
        for card in cards:
            console.print(f"  [green]>[/green] {card.name}")
        console.print(
            f"\n[bold green]완료![/bold green] {len(cards)}개 카드 생성 -> {project.carousel_dir}"
        )
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


@pipeline.command("add-subtitles")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--project", "project_name", required=True, help="프로젝트 이름")
@requires_profile("base")
def pipeline_add_subtitles(
    ctx: click.Context, input_path: Path, project_name: str
) -> None:
    """영상에 자막과 B-roll을 추가합니다 (전체 파이프라인)."""
    from entities.project.model import Project
    from pipelines.add_subtitles import run_add_subtitles

    config = ctx.obj["config"]
    project = Project(name=project_name)
    project.ensure_dirs()

    console.print(
        Panel(
            f"[bold]프로젝트:[/bold] {project_name}\n"
            f"[bold]입력 영상:[/bold] {input_path}\n"
            f"[bold]출력:[/bold] {project.output_dir}",
            title="Add Subtitles 파이프라인",
        )
    )

    try:
        output = run_add_subtitles(
            project=project,
            config=config,
            video_path=input_path,
        )
        console.print(f"\n[bold green]완료![/bold green] 영상: {output}")
    except Exception as e:
        console.print(f"\n[bold red]오류:[/bold red] {e}")
        raise click.Abort()


def _parse_srt_file(srt_path: Path) -> SubtitleTrack:
    """SRT 파일을 SubtitleTrack으로 파싱."""
    import re

    from entities.subtitle.model import SubtitleSegment, SubtitleTrack

    content = srt_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\n+", content.strip())

    segments: list[SubtitleSegment] = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        index = int(lines[0].strip())
        time_match = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            lines[1].strip(),
        )
        if not time_match:
            continue

        h1, m1, s1, ms1, h2, m2, s2, ms2 = time_match.groups()
        start = int(h1) * 3600 + int(m1) * 60 + int(s1) + int(ms1) / 1000
        end = int(h2) * 3600 + int(m2) * 60 + int(s2) + int(ms2) / 1000
        text = "\n".join(lines[2:])

        segments.append(SubtitleSegment(index=index, start=start, end=end, text=text))

    return SubtitleTrack(segments=segments)


def main() -> None:
    """CLI 메인 진입점."""
    cli()


if __name__ == "__main__":
    main()
