from gomi.common import CardTemplate, find_js_files, find_url_imports

MODEL_CSS = """
@charset "UTF-8";
@import url("_ajt_japanese_24.7.14.1.css");
@import url("_tsc_card_css.css");
@font-face {
    font-family: "KanjiStrokeOrders";
    src: url("_kso.woff2");
}
@font-face {
    font-family: "Local Mincho";
    src: url("_yumin.woff2");
}
"""

TEMPLATES = [
    CardTemplate(
        name="test",
        front="""
        <main>
            <script src="_script.js"></script>
        </main>
        <script src="_ajt_japanese.js"></script>
        """,
        back="""
        <div class="test"><script src='my_script.js'></script></div>
        <script src="_ajt_japanese.js"></script>
        """,
    )
]


def test_find_referenced_urls() -> None:
    result = find_url_imports(MODEL_CSS)
    assert result == {"_ajt_japanese_24.7.14.1.css", "_kso.woff2", "_yumin.woff2", "_tsc_card_css.css"}


def test_find_js_files() -> None:
    result = find_js_files(TEMPLATES)
    assert result == {"_script.js", "_ajt_japanese.js", "my_script.js"}
