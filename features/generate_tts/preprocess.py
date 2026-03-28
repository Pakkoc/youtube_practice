"""TTS 텍스트 전처리 (URL/확장자, 발음 사전, 숫자 정규화, 언어 감지)."""

from __future__ import annotations

import re

from shared.lib.logger import get_logger

logger = get_logger()

# 숫자 감지: 아라비아 숫자 포함 여부
_NUMBER_PATTERN = re.compile(r"\d")

# ──────────────────────────────────────────────
# 규칙 기반 한국어 숫자 정규화
# ──────────────────────────────────────────────

# 한자어 수사 (Sino-Korean)
_SINO_DIGITS = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_SINO_SMALL = ["", "십", "백", "천"]
_SINO_LARGE = ["", "만", "억", "조", "경"]

# 고유어 수사 관형형 (Native Korean, modified forms before counters)
_NATIVE_ONES = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
_NATIVE_TENS = ["", "열", "스무", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]

# 전화번호/코드/소수점 이하 숫자 읽기
_DIGIT_READ = ["공", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]

# 고유어 수사를 쓰는 조수사 (1~99 범위만 고유어, 100 이상은 한자어)
_NATIVE_COUNTERS = frozenset({
    "개", "명", "살", "마리", "잔", "벌", "대", "채", "권",
    "시", "곳", "가지", "그루", "쌍", "줄", "통", "포기", "켤레",
    "송이", "자루", "척", "편", "배",
})

# 만/억/조 값
_MULT_VALUES = {"만": 10_000, "억": 100_000_000, "조": 1_000_000_000_000}

# 기호 단위 → 한글 발음
_SYMBOL_PRONUNCIATION: dict[str, str] = {
    "%": "퍼센트",
    "km": "킬로미터", "kg": "킬로그램",
    "cm": "센티미터", "mm": "밀리미터",
    "m": "미터", "g": "그램", "L": "리터",
    "GB": "기가바이트", "MB": "메가바이트",
    "KB": "킬로바이트", "TB": "테라바이트",
    "GHz": "기가헤르츠", "MHz": "메가헤르츠",
    "kHz": "킬로헤르츠", "Hz": "헤르츠",
    "ml": "밀리리터", "cc": "씨씨",
}

# 전화번호 패턴: 010-1234-5678, 02-123-4567
_PHONE_RE = re.compile(r"\b(\d{2,4})-(\d{3,4})(?:-(\d{3,4}))?\b")

# 숫자 표현 패턴
# Groups: 1=$, 2=int, 3=decimal, 4=space, 5=만억조, 6=space, 7=unit
_NUM_EXPR_RE = re.compile(
    r"(?<![a-zA-Z\d])"  # 영문자/숫자 뒤가 아닐 때만 (B612 등 방지)
    r"(\$)?"  # 1: $ prefix
    r"(\d[\d,]*)"  # 2: integer (with commas)
    r"(?:\.(\d+))?"  # 3: decimal
    r"(\s*)"  # 4: space
    r"(만|억|조)?"  # 5: Korean multiplier
    r"(\s*)"  # 6: space
    r"("  # 7: unit/counter (longest first)
    r"시간|퍼센트"
    r"|킬로미터|킬로그램|센티미터|밀리미터"
    r"|GHz|MHz|kHz|Hz"
    r"|GB|MB|KB|TB"
    r"|km|kg|cm|mm|ml|cc|hp"
    r"|달러|위안|유로"
    r"|가지|마리|켤레|그루|포기|송이|자루"
    r"|단계"
    r"|엔|원"
    r"|년|월|일|시|분|초"
    r"|개|명|살|잔|벌|대|채|권|번|곳"
    r"|장|절|호|층|항|등|배|편|종|건|점|줄|칸|통|쌍|척"
    r"|미터|그램"
    r"|m|g|L"
    r"|%"
    r")?"
    r"(?![a-zA-Z])"  # 영문자가 바로 뒤따르지 않을 때만 (3D 등 방지)
)


def _sino_korean(n: int) -> str:
    """정수 → 한자어 수사. 0이면 '영'."""
    if n == 0:
        return "영"
    parts: list[str] = []
    large_idx = 0
    while n > 0:
        group = n % 10_000
        n //= 10_000
        g = group
        group_str = ""
        for i in range(4):
            d = g % 10
            g //= 10
            if d == 0:
                continue
            if i == 0:  # 일의 자리
                group_str = _SINO_DIGITS[d] + group_str
            else:  # 십/백/천: 일 생략 (십, 백, 천 — not 일십, 일백, 일천)
                prefix = "" if d == 1 else _SINO_DIGITS[d]
                group_str = prefix + _SINO_SMALL[i] + group_str
        if group_str:
            parts.append(group_str + _SINO_LARGE[large_idx])
        large_idx += 1
    return "".join(reversed(parts))


def _native_korean(n: int) -> str:
    """1~99 → 관형형 고유어 수사 (한, 두, 세...). 범위 밖이면 한자어 fallback."""
    if n < 1 or n > 99:
        return _sino_korean(n)
    tens, ones = divmod(n, 10)
    t = _NATIVE_TENS[tens]
    o = _NATIVE_ONES[ones]
    # 스무: 단독 사용 (스무 개). 스물: 합성 (스물한 개)
    if tens == 2 and ones > 0:
        t = "스물"
    return t + o


def _read_digits(s: str) -> str:
    """숫자 문자열을 한 자리씩 읽기 (전화번호/소수점 이하)."""
    return "".join(_DIGIT_READ[int(c)] for c in s if c.isdigit())


def _replace_phone(m: re.Match) -> str:
    """전화번호 → 한 자리씩 읽기 (공일공 일이삼사 오육칠팔)."""
    parts = [_read_digits(m.group(1)), _read_digits(m.group(2))]
    if m.group(3):
        parts.append(_read_digits(m.group(3)))
    return " ".join(parts)


def _replace_number(m: re.Match) -> str:
    """숫자 표현 → 한국어 발음."""
    dollar = m.group(1)
    int_str = m.group(2)
    dec_str = m.group(3)
    multiplier = m.group(5)
    space2 = m.group(6) or ""
    unit = m.group(7) or ""

    int_val = int(int_str.replace(",", ""))

    # 만/억/조 곱하기
    if multiplier:
        mv = _MULT_VALUES[multiplier]
        if dec_str:
            int_val = int(float(f"{int_val}.{dec_str}") * mv)
            dec_str = None  # 소수점은 multiplier에 흡수됨
        else:
            int_val *= mv

    # 고유어 vs 한자어 결정 (1~99 + 고유어 조수사일 때만 고유어)
    use_native = unit in _NATIVE_COUNTERS and 1 <= int_val <= 99

    num_text = _native_korean(int_val) if use_native else _sino_korean(int_val)

    # 소수점 (multiplier에 흡수되지 않은 경우)
    if dec_str:
        num_text += "점" + _read_digits(dec_str)

    # 단위 결합
    if dollar:
        return num_text + "달러"
    if unit in ("%", "퍼센트"):
        return num_text + "퍼센트"
    if unit:
        pron = _SYMBOL_PRONUNCIATION.get(unit, unit)
        return num_text + space2 + pron
    return num_text

# 도메인/파일 확장자 → 한글 발음 매핑 (긴 것부터 매칭하도록 정렬)
_EXTENSION_PRONUNCIATION: dict[str, str] = {
    # 도메인
    ".com": "닷컴",
    ".io": "닷아이오",
    ".ai": "닷에이아이",
    ".dev": "닷데브",
    ".org": "닷오알지",
    ".net": "닷넷",
    ".co": "닷씨오",
    ".kr": "닷케이알",
    # 코드/설정
    ".yaml": "닷야믈",
    ".yml": "닷야믈",
    ".json": "닷제이슨",
    ".tsx": "닷티에스엑스",
    ".jsx": "닷제이에스엑스",
    ".ts": "닷티에스",
    ".js": "닷제이에스",
    ".py": "닷파이",
    ".md": "닷엠디",
    ".txt": "닷텍스트",
    ".env": "닷엔브",
    ".html": "닷에이치티엠엘",
    ".css": "닷씨에스에스",
    ".csv": "닷씨에스브이",
    # 문서
    ".pdf": "닷피디에프",
    ".pptx": "닷피피티엑스",
}


# URL 정규화 패턴 (모듈 레벨 컴파일)
# 슬래시 명령어 범용 패턴: 공백/문장시작 뒤 /영단어 → "슬래시 영단어"
# 사전에 등록된 명령어는 Step 1에서 이미 치환되므로, 남은 것만 잡음
_SLASH_CMD_RE = re.compile(r"(?:^|(?<=\s))(/([a-zA-Z][\w-]*))")

_URL_PROTOCOL_RE = re.compile(r"https?://(www\.)?")
_URL_WWW_RE = re.compile(r"\bwww\.")
_URL_PATH_RE = re.compile(r"\.(com|io|ai|dev|org|net|co|kr)/\S+")

# 확장자 일괄 치환용 컴파일 패턴 (긴 것부터 매칭)
_EXT_KEYS_SORTED = sorted(_EXTENSION_PRONUNCIATION, key=len, reverse=True)
_EXT_PATTERN = re.compile(
    r"(?<=[a-zA-Z0-9])("
    + "|".join(re.escape(e) for e in _EXT_KEYS_SORTED)
    + r")(?=[^a-zA-Z0-9.]|$)"
)


def _replace_ext(m: re.Match) -> str:
    """확장자 매치 → 한글 발음 치환."""
    return " " + _EXTENSION_PRONUNCIATION[m.group(1)]


def detect_language_code(text: str, default: str = "ko") -> str:
    """텍스트 내 한글/영어 비율 기반으로 language_code 결정.

    한글(가-힣)이 포함되어 있으면 영어가 80% 초과일 때만 "en" 반환.
    한글이 없으면 ASCII 알파벳 50% 초과 시 "en" 반환.
    한국어 기술 콘텐츠에서 영어 용어가 섞인 정도로는 "en"이 되지 않음.

    Args:
        text: 입력 텍스트.
        default: 기본 language_code.

    Returns:
        "en" 또는 default.
    """
    non_space = [c for c in text if not c.isspace()]
    if not non_space:
        return default
    hangul_count = sum(1 for c in non_space if "\uac00" <= c <= "\ud7af")
    alpha_count = sum(1 for c in non_space if c.isascii() and c.isalpha())
    if hangul_count > 0:
        # 한글이 있으면 영어가 압도적(>80%)일 때만 "en"
        total_lang = hangul_count + alpha_count
        if total_lang == 0:
            return default
        return "en" if alpha_count / total_lang > 0.8 else default
    # 한글 없음 → ASCII 알파벳 50% 초과 시 "en"
    return "en" if alpha_count / len(non_space) > 0.5 else default


def has_numbers(text: str) -> bool:
    """텍스트에 아라비아 숫자가 포함되어 있는지 확인."""
    return bool(_NUMBER_PATTERN.search(text))


def normalize_numbers_for_tts(text: str) -> str:
    """숫자가 포함된 텍스트를 한국어 발음으로 변환 (규칙 기반, 결정론적).

    예시:
        "10만 권" -> "십만 권"
        "30%" -> "삼십퍼센트"
        "2024년" -> "이천이십사년"
        "1,500명" -> "천오백명"
        "$100" -> "백달러"
        "3.14" -> "삼점일사"
        "5개" -> "다섯개"
        "010-1234-5678" -> "공일공 일이삼사 오육칠팔"

    Args:
        text: 숫자가 포함된 원본 텍스트.

    Returns:
        숫자가 한국어로 변환된 텍스트.
    """
    if not has_numbers(text):
        return text

    # 1단계: 전화번호 (하이픈 연결) → 한 자리씩 읽기
    result = _PHONE_RE.sub(_replace_phone, text)

    # 2단계: 숫자 + 단위 → 한국어 발음
    result = _NUM_EXPR_RE.sub(_replace_number, result)

    if result != text:
        logger.debug("숫자 정규화: '%s' -> '%s'", text[:60], result[:60])

    return result


def normalize_urls_and_extensions(text: str) -> str:
    """URL 프로토콜 제거 + 도메인/파일 확장자를 한글 발음으로 변환.

    예시:
        "https://n8n.io" → "n8n 닷아이오"
        "SKILL.md 파일" → "SKILL 닷엠디 파일"
        "agentskills.io" → "agentskills 닷아이오"

    확장자 앞에 영숫자(ASCII)가 있어야 매칭되므로
    한국어 문장 끝 마침표(합니다.)와 혼동하지 않습니다.

    Args:
        text: 원본 텍스트.

    Returns:
        확장자가 한글 발음으로 변환된 텍스트.
    """
    result = text

    # URL 프로토콜 제거: https://www. → ""
    result = _URL_PROTOCOL_RE.sub("", result)
    result = _URL_WWW_RE.sub("", result)

    # URL 경로 제거: vercel.com/dashboard → vercel.com
    result = _URL_PATH_RE.sub(r".\1", result)

    # 확장자 치환 (단일 컴파일 패턴으로 일괄 처리)
    result = _EXT_PATTERN.sub(_replace_ext, result)

    return result


def preprocess_for_tts(text: str, tts_dictionary: dict[str, str] | None = None) -> str:
    """TTS 생성 전 텍스트 전처리.

    1. URL/확장자 → 한글 발음 (n8n.io → n8n 닷아이오)
    2. 발음 사전 치환 (신조어/브랜드명 → 한글 발음)
    3. 숫자 → 한국어 발음 변환 (규칙 기반, 결정론적)

    Args:
        text: 원본 텍스트.
        tts_dictionary: TTS 발음 사전. None이면 사전 치환 건너뜀.

    Returns:
        전처리된 TTS용 텍스트.
    """
    result = text

    # Step 1: 발음 사전 치환 (URL 정규화보다 먼저 → "SKILL.md", "agentskills.io" 등 전체 토큰 매칭)
    if tts_dictionary:
        from features.normalize_text import apply_tts_dictionary

        result = apply_tts_dictionary(result, tts_dictionary)

    # Step 1.5: 사전에 없는 /명령어 → "슬래시 명령어" 범용 변환
    result = _SLASH_CMD_RE.sub(lambda m: "슬래시 " + m.group(2), result)

    # Step 2: URL/확장자 정규화 (사전에 없는 도메인/확장자를 한글 발음으로 변환)
    result = normalize_urls_and_extensions(result)

    # Step 3: 숫자 정규화
    result = normalize_numbers_for_tts(result)

    return result
