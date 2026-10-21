import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

# screensフォルダの1つ上にあるプロジェクトフォルダを基準に、保存先を決めます。
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "company_research.csv"


def save_company_research(company_name, company_url, selections, research):
    """登録内容をCSVに1件追記します。見出しは新規作成時だけ書きます。"""
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not CSV_PATH.exists()
    registered_at = datetime.now(timezone(timedelta(hours=9)))
    headers = [
        "登録日時",
        "企業名",
        "企業URL",
        *[
            f"STEP{step}_選択{item}"
            for step in range(1, 4)
            for item in range(1, 4)
        ],
        "企業研究内容",
    ]
    row = [
        registered_at.strftime("%Y-%m-%d %H:%M:%S"),
        company_name,
        company_url,
        *[item for items in selections.values() for item in items],
        research,
    ]

    # UTF-8 BOM付きにすると、Excelで日本語が文字化けしにくくなります。
    # newline=""とcsv.writerで、改行やカンマを含む長文も正しく保存します。
    with CSV_PATH.open("a", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if is_new_file:
            writer.writerow(headers)
        writer.writerow(row)


def load_company_list():
    """CSVから、一覧に表示する企業名と登録日時だけを取り出します。"""
    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [
                {"企業名": row["企業名"], "登録日時": row["登録日時"]}
                for row in reader
            ]
    except FileNotFoundError:
        return []


if st.button("ホームへ戻る"):
    st.switch_page("screens/home.py")

st.title("エンジョブ企業研究")
st.header("企業研究の入力")
st.caption("自己分析Aの各STEPで3項目ずつ選び、企業研究を入力してください。")

# 各STEPの選択肢をまとめています。
step_options = {
    "STEP1｜業界選びの価値観": [
        "景気に左右されにくく、長く安定して働ける業界がいい",
        "これから市場が伸びていきそうな業界で働きたい",
        "社会や人々の生活に欠かせない仕事に関わりたい",
        "普段の生活で目にする商品やサービスに関わりたい",
        "多くの人や社会に影響を与える大きな仕事がしたい",
        "新しいサービスや技術が次々生まれる業界に関わりたい",
        "将来も使える専門知識やスキルを身につけたい",
        "若いうちから成長し、高い収入や市場価値を目指したい",
        "人の成長や人生の選択を支える仕事に関わりたい",
        "企業や経営者の課題を解決する仕事に関わりたい",
        "自分たちが作った製品や技術が世の中に残る仕事がしたい",
        "海外や世界と関わる仕事がしたい",
        "自分が住む地域や地元の発展に関わりたい",
        "エンタメ・スポーツ・ファッションなど、自分の好きな分野に関わりたい",
    ],
    "STEP2｜特性・強み": [
        "初対面の人とも比較的すぐに話せる",
        "人の話を聞いたり、相談に乗ったりすることが多い",
        "人に何かを説明したり、分かりやすく伝えることが得意",
        "周りの人を誘ったり、巻き込んで何かを進めることが多い",
        "誰かに勝ちたい、目標を達成したいと思うと頑張れる",
        "自分で考えて動く方が好きで、指示を待つのは苦手",
        "計画を立てて、コツコツ順番に進めることが得意",
        "細かいミスや違いによく気づく方だ",
        "数字やデータを見て考えることに抵抗がない",
        "「なぜこうなるんだろう？」と原因を考えることが好き",
        "新しいアイデアや企画を考えることが好き",
        "自分が作ったものが形になると嬉しい",
        "一つのことを深く調べたり、詳しくなることが好き",
        "困っている人や、チームを裏側から支えることにやりがいを感じる",
    ],
    "STEP3｜働く環境・会社選び": [
        "仕事だけでなく、自分の時間もしっかり確保したい",
        "できれば地元・希望する地域で長く働きたい",
        "リモートやフレックスなど、働く時間や場所を柔軟に選びたい",
        "給与や福利厚生など、待遇がしっかりしている会社がいい",
        "会社の経営が安定していて、安心して長く働ける会社がいい",
        "会社と一緒に成長していくような、勢いのある環境がいい",
        "研修や教育制度が整っていて、最初はしっかり教えてもらいたい",
        "若いうちから仕事を任され、自分で考えて動きたい",
        "年齢に関係なく、頑張った人が評価される会社がいい",
        "個人で競うより、チームで協力しながら仕事をしたい",
        "仲間同士の距離が近く、相談しやすい会社がいい",
        "役割やルールが明確で、ある程度決まった進め方がある方が安心する",
        "いろいろな仕事を経験するより、一つの分野を深く極めたい",
        "最初はいろいろな仕事を経験して、自分に合うものを見つけたい",
    ],
}

# フォームの中の入力は、「登録する」を押したときにまとめて受け取ります。
with st.form("company_research", enter_to_submit=False):
    company_name = st.text_input("企業名（必須）")
    company_url = st.text_input("企業URL", placeholder="https://example.com")

    st.subheader("自己分析A")
    selections = {}
    for step, options in step_options.items():
        selections[step] = st.multiselect(
            step,
            options,
            max_selections=3,
            placeholder="3項目選択してください",
            help="必ず3項目選んでください。4項目以上は選べません。",
            select_all=False,
            wrap=True,
        )

    research = st.text_area("企業発見・比較用企業研究（必須）", height=280)
    submitted = st.form_submit_button(
        "登録する", type="primary", width="stretch"
    )

# 必須項目と選択数を確認し、問題がない場合だけCSVに保存します。
if submitted:
    errors = []
    if not company_name.strip():
        errors.append("企業名を入力してください。")
    if not research.strip():
        errors.append("企業研究内容を入力してください。")

    invalid_steps = [step for step, items in selections.items() if len(items) != 3]
    for step in invalid_steps:
        errors.append(f"{step}は必ず3項目選択してください（現在{len(selections[step])}項目）。")

    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            save_company_research(company_name, company_url, selections, research)
        except OSError as error:
            st.error(f"CSVに保存できませんでした：{error}")
        else:
            st.success("CSVに保存しました。")
            st.divider()
            st.subheader("入力内容の確認")
            st.markdown("**企業名**")
            st.text(company_name)
            st.markdown("**企業URL**")
            st.text(company_url or "（未入力）")
            for step, items in selections.items():
                st.markdown(f"**自己分析A {step}**")
                for item in items:
                    st.text(f"・{item}")
            st.markdown("**企業発見・比較用企業研究**")
            st.text(research)


# 保存処理の後にCSVを読み込むので、新しく登録した企業も一覧に表示されます。
st.divider()
st.header("登録済み企業一覧")
try:
    company_list = load_company_list()
except (OSError, UnicodeError, csv.Error) as error:
    st.error(f"企業一覧を読み込めませんでした：{error}")
else:
    if company_list:
        st.table(company_list, hide_index=True)
    else:
        st.info("まだ企業研究が登録されていません")
