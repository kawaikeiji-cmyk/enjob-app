import csv
from pathlib import Path

import streamlit as st

# 登録画面と同じCSVを読み込みます。検索では書き込みません。
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "company_research.csv"


def search_companies(selections):
    """企業ごとの最高一致数・その投稿のSTEP別一致数・投稿件数を返します。"""
    companies = {}
    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                return []
            required_columns = {"企業名"} | {
                f"STEP{step}_選択{item}"
                for step in range(1, 4)
                for item in range(1, 4)
            }
            if not required_columns.issubset(reader.fieldnames):
                raise ValueError("CSVに企業名または自己分析Aの列がありません。")

            for row in reader:
                company_name = row["企業名"]
                if not company_name or not company_name.strip():
                    continue

                # 同じSTEPの中だけで比較します。選んだ順番は問いません。
                step_matches = []
                for step in range(1, 4):
                    registered_items = {
                        row[f"STEP{step}_選択{item}"] for item in range(1, 4)
                    }
                    matches = len(set(selections[step]) & registered_items)
                    step_matches.append(matches)
                total_matches = sum(step_matches)

                company = companies.setdefault(
                    company_name,
                    {
                        "企業名": company_name,
                        "一致数": -1,
                        "STEP別一致数": [],
                        "企業研究件数": 0,
                    },
                )
                company["企業研究件数"] += 1
                # STEPごとの最高値を混ぜず、最高点の投稿1件の内訳を使います。
                # 同点の場合は、CSVで先に登録された投稿の内訳を保持します。
                if total_matches > company["一致数"]:
                    company["一致数"] = total_matches
                    company["STEP別一致数"] = step_matches
    except FileNotFoundError:
        return []

    # 同じ類似度の場合は、企業名の順に並べます。
    return sorted(
        companies.values(), key=lambda company: (-company["一致数"], company["企業名"])
    )


if st.button("ホームへ戻る"):
    st.switch_page("screens/home.py")

st.title("企業検索")
st.caption("自己分析Aの各STEPで3項目ずつ選ぶと、類似度の高い企業を探せます。")

# 企業登録画面と同じ14項目を、同じ順番で表示します。
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

with st.form("company_search", enter_to_submit=False):
    st.subheader("自己分析A")
    selections = {}
    for step_number, (label, options) in enumerate(step_options.items(), start=1):
        selections[step_number] = st.multiselect(
            label,
            options,
            key=f"search_step_{step_number}",
            max_selections=3,
            placeholder="3項目選択してください",
            help="必ず3項目選んでください。4項目以上は選べません。",
            select_all=False,
            wrap=True,
        )
    submitted = st.form_submit_button(
        "企業を検索する", type="primary", width="stretch"
    )

if submitted:
    invalid_steps = [step for step, items in selections.items() if len(items) != 3]
    if invalid_steps:
        for step in invalid_steps:
            st.error(f"STEP{step}は必ず3項目選択してください（現在{len(selections[step])}項目）。")
    else:
        try:
            companies = search_companies(selections)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            st.error(f"企業研究データを読み込めませんでした：{error}")
        else:
            st.divider()
            st.header("検索結果")
            if not companies:
                st.info("まだ企業研究が登録されていません")
            else:
                st.caption(
                    "類似度は一致数 ÷ 9 × 100です。同じ企業は最高類似度の投稿を表示します。"
                )
                result_rows = [
                    {
                        "企業名": company["企業名"],
                        "類似度": f"{company['一致数'] / 9 * 100:.1f}%",
                        "STEP1の一致数": f"{company['STEP別一致数'][0]}/3",
                        "STEP2の一致数": f"{company['STEP別一致数'][1]}/3",
                        "STEP3の一致数": f"{company['STEP別一致数'][2]}/3",
                        "企業研究件数": company["企業研究件数"],
                    }
                    for company in companies
                ]
                st.table(result_rows, hide_index=True)
