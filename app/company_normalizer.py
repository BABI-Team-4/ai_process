"""
기업명 정규화 모듈

사용자가 입력한 기업명을 DB에 저장된 표준 기업명으로 변환.

변환 전략 (3단계):
  1. 전처리: 소문자 + 공백·특수문자 제거
  2. 정확/별칭 매칭: ALIAS_MAP dict lookup (O(1))
  3. Fuzzy 매칭: difflib로 가장 유사한 후보 반환 (임계값 0.6)
"""

import difflib

# ── 표준 기업명 (DB 저장값과 동일) ────────────────────────────────────────────

SUPPORTED_COMPANIES: list[str] = [
    "삼성전자", "현대자동차", "SK하이닉스", "LG전자", "포스코",
    "한국전력", "농협은행", "기업은행", "신한은행", "우리은행", "국민은행", "하나은행",
]

# ── 별칭 테이블 ───────────────────────────────────────────────────────────────
# CSV 분석 기준: 실제로 DB에 들어온 112개 variants 포함

COMPANY_ALIASES: dict[str, list[str]] = {
    "삼성전자": [
        "삼성전자", "삼성전자㈜", "삼성전자 ", "삼성전자DX", "삼성전자DX ",
        "삼성전자DS", "삼성전자 DX부문", "삼성전자 LSI", "삼성전자 S.LSI",
        "삼성전자 sst", "삼성전자 (TSP센터)", "삼성전자로지텍", "삼성전자로지텍(주)",
        "삼성전자서비스", "삼성전자서비스(주)", "삼성전자판매", "삼성전자판매(주)",
        "samsung", "samsung electronics",
    ],
    "현대자동차": [
        "현대자동차", "현대자동차㈜", "현대자동차 ", "현대차", "현대",
        "hyundai", "현대자동차그룹",
    ],
    "SK하이닉스": [
        "SK하이닉스", "SK하이닉스(주)", "SK 하이닉스", "Sk하이닉스",
        "sk하이닉스", "sk 하이닉스", "하이닉스", "skhynix", "sk hynix",
        "SK하이닉스 청년 Hy-Five (스크린에스피이코리아)",
        "SK하이닉스 청년 Hy-five (오로스테크놀로지)",
        "SK하이닉스 청년희망나눔",
    ],
    "LG전자": [
        "LG전자", "LG전자/화학", "lg전자", "LG 전자", "엘지전자", "엘지",
        "lg electronics",
    ],
    "포스코": [
        "포스코", "㈜포스코", "포스코 ", "포스코홀딩스", "POSCO", "posco",
        "포항제철",
    ],
    "한국전력": [
        "한국전력", "한국전력공사", "한전", "KEPCO", "kepco", "한국 전력",
        "한국전력기술", "한국전력기술주식회사", "한전 KPS", "한국전력거래소",
    ],
    "농협은행": [
        "농협은행", "NH농협은행", "농협", "NH농협", "nh농협", "농협은행IT부문",
    ],
    "기업은행": [
        "기업은행", "IBK기업은행", "IBK 기업은행", "IBK", "ibk",
        "중소기업은행",
    ],
    "신한은행": [
        "신한은행", "㈜신한은행", "신한",
    ],
    "우리은행": [
        "우리은행", "㈜우리은행", "우리",
    ],
    "국민은행": [
        "국민은행", "KB국민은행", "KB 국민은행", "㈜국민은행", "KB국민",
        "KB", "kb", "kb국민은행",
    ],
    "하나은행": [
        "하나은행", "하나",
    ],
}


# ── 내부 유틸 ─────────────────────────────────────────────────────────────────

def _normalize_key(s: str) -> str:
    """소문자 변환 + 공백·특수접미사 제거한 비교용 키"""
    s = s.lower().strip()
    s = s.replace(" ", "").replace("　", "")
    # 법인 접미사 제거 (비교용, 원본 건드리지 않음)
    for suffix in ("(주)", "㈜", "주식회사", "(주식회사)", "(유)", "유한회사"):
        s = s.replace(suffix, "")
    return s


# 정규화 키 → 표준 기업명 역매핑 (모듈 로드 시 1회 빌드)
_ALIAS_MAP: dict[str, str] = {}
for _canonical, _aliases in COMPANY_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_MAP[_normalize_key(_alias)] = _canonical
# 표준명 자체도 등록 (대소문자 변형 대응)
for _canonical in SUPPORTED_COMPANIES:
    _ALIAS_MAP[_normalize_key(_canonical)] = _canonical


# ── 공개 API ──────────────────────────────────────────────────────────────────

def normalize_company(name: str) -> str | None:
    """
    사용자 입력 기업명 → DB 표준 기업명으로 변환.

    Returns
    -------
    str  : 표준 기업명 (예: "SK하이닉스")
    None : 지원하지 않는 기업
    """
    if not name:
        return None

    key = _normalize_key(name)

    # 1단계: 정확/별칭 매칭
    if key in _ALIAS_MAP:
        return _ALIAS_MAP[key]

    # 2단계: Fuzzy 매칭
    candidates = list(_ALIAS_MAP.keys())
    matches = difflib.get_close_matches(key, candidates, n=1, cutoff=0.6)
    if matches:
        return _ALIAS_MAP[matches[0]]

    return None


def get_supported_companies() -> list[str]:
    return SUPPORTED_COMPANIES.copy()
