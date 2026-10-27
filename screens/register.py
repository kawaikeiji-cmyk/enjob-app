from datetime import datetime, timedelta, timezone

import streamlit as st

from supabase_store import (
    CompanyResearchError,
    load_company_research,
    save_company_research,
)


def format_registered_at(value):
    """Supabaseの登録日時を、これまでと同じ日本時間の表示にします。"""
    if not value:
        return "（未設定）"
    registered_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if registered_at.tzinfo is None:
        registered_at = registered_at.replace(tzinfo=timezone.utc)
    return registered_at.astimezone(timezone(timedelta(hours=9))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def load_company_list():
    """Supabaseから、一覧に表示する企業名と登録日時を読み込みます。"""
    rows = load_company_research("company_name,created_at")
    return [
        {
            "企業名": row["company_name"],
            "登録日時": format_registered_at(row["created_at"]),
        }
        for row in rows
    ]


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

# 必須項目と選択数を確認し、問題がない場合だけSupabaseに保存します。
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
        except CompanyResearchError as error:
            st.error(str(error))
        else:
            st.success("企業研究を保存しました。")
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


# 保存処理の後に読み込むので、新しく登録した企業も一覧に表示されます。
st.divider()
st.header("登録済み企業一覧")
try:
    company_list = load_company_list()
except CompanyResearchError as error:
    st.error(str(error))
else:
    if company_list:
        st.table(company_list, hide_index=True)
    else:
        st.info("まだ企業研究が登録されていません")
