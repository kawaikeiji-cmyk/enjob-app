import streamlit as st

from supabase_store import CompanyResearchError, load_company_research


def search_companies(selections):
    """投稿ごとの一致数を計算し、企業ごとにまとめて返します。"""
    companies = {}
    rows = load_company_research(
        "company_name,company_url,step1_choices,step2_choices,step3_choices,research_text"
    )
    for row in rows:
        company_name = row["company_name"]
        if not company_name or not company_name.strip():
            continue

        # 同じSTEPの中だけで比較します。選んだ順番は問いません。
        step_matches = []
        for step in range(1, 4):
            registered_items = set(row[f"step{step}_choices"] or [])
            matches = len(set(selections[step]) & registered_items)
            step_matches.append(matches)
        total_matches = sum(step_matches)

        company = companies.setdefault(
            company_name,
            {
                "企業名": company_name,
                "並び替え用一致数": 0,
                "企業研究": [],
            },
        )
        company["企業研究"].append(
            {
                "一致数": total_matches,
                "STEP別一致数": step_matches,
                "企業URL": row["company_url"] or "",
                "STEP別選択内容": [
                    list(row[f"step{step}_choices"] or []) for step in range(1, 4)
                ],
                "企業研究内容": row["research_text"] or "",
            }
        )
        # 企業の最高一致数は並び替えだけに使い、画面には表示しません。
        company["並び替え用一致数"] = max(
            company["並び替え用一致数"], total_matches
        )

    for company in companies.values():
        company["企業研究"].sort(key=lambda post: -post["一致数"])
        company["企業研究件数"] = len(company["企業研究"])

    # 同じ類似度の場合は、企業名の順に並べます。
    return sorted(
        companies.values(),
        key=lambda company: (-company["並び替え用一致数"], company["企業名"]),
    )


def show_more_posts(company_index):
    """表示件数を3件増やします。検索結果は再取得せず、そのまま保持します。"""
    visible_counts = st.session_state["company_search_visible_posts"]
    visible_counts[company_index] = visible_counts.get(company_index, 3) + 3


def render_research(post, number, widget_key):
    """投稿1件の一致度と内容を、スマートフォン向けに縦1列で表示します。"""
    with st.container(border=True):
        st.markdown(f"**企業研究 {number}**")
        st.markdown(f"**投稿者との類似度：{post['一致数'] / 9 * 100:.1f}%**")
        st.text(
            "　".join(
                f"STEP{step}：{matches}/3"
                for step, matches in enumerate(post["STEP別一致数"], start=1)
            )
        )
        st.markdown("**企業URL**")
        st.text(post["企業URL"] or "（未入力）")
        for step, choices in enumerate(post["STEP別選択内容"], start=1):
            st.markdown(f"**STEP{step}の選択内容**")
            st.text("\n".join(f"・{item}" for item in choices) or "（未入力）")

        st.markdown("**企業研究内容**")
        research = post["企業研究内容"]
        show_full = False
        if len(research) > 300:
            show_full = st.toggle("全文を表示", key=f"{widget_key}_full_text")
        if len(research) > 300 and not show_full:
            st.text(research[:300] + "…")
        else:
            st.text(research or "（未入力）")


if st.button("ホームへ戻る"):
    st.session_state.pop("company_search_results", None)
    st.session_state.pop("company_search_visible_posts", None)
    st.switch_page("screens/home.py")

st.title("企業検索")
st.caption("自己分析Aの各STEPで3項目ずつ選び、投稿者との一致度から企業研究を探せます。")

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
    # 新しい検索では、以前の結果や追加表示件数をリセットします。
    st.session_state.pop("company_search_results", None)
    st.session_state["company_search_visible_posts"] = {}
    st.session_state["company_search_generation"] = (
        st.session_state.get("company_search_generation", 0) + 1
    )
    invalid_steps = [step for step, items in selections.items() if len(items) != 3]
    if invalid_steps:
        for step in invalid_steps:
            st.error(f"STEP{step}は必ず3項目選択してください（現在{len(selections[step])}項目）。")
    else:
        try:
            companies = search_companies(selections)
        except CompanyResearchError as error:
            st.error(str(error))
        else:
            st.session_state["company_search_results"] = companies

# ボタンや全文表示の操作で再実行されても、検索結果を残します。
if "company_search_results" in st.session_state:
    companies = st.session_state["company_search_results"]
    st.divider()
    st.header("検索結果")
    if not companies:
        st.info("まだ企業研究が登録されていません")
    else:
        st.caption(
            "企業名をタップすると、企業研究の投稿ごとの一致度と内容が開きます。"
            "類似度は、投稿者とあなたの自己分析Aの一致数 ÷ 9 × 100です。"
        )
        generation = st.session_state["company_search_generation"]
        visible_counts = st.session_state["company_search_visible_posts"]
        for company_index, company in enumerate(companies):
            company_key = f"search_company_{generation}_{company_index}"
            with st.expander(
                f"{company['企業名']} ｜ 企業研究 {company['企業研究件数']}件",
                key=company_key,
            ):
                posts = company["企業研究"]
                visible_count = min(visible_counts.get(company_index, 3), len(posts))
                st.caption(f"投稿者との類似度が高い順に {visible_count} / {len(posts)}件を表示")
                for post_index, post in enumerate(posts[:visible_count]):
                    render_research(
                        post,
                        post_index + 1,
                        f"{company_key}_post_{post_index}",
                    )
                if visible_count < len(posts):
                    st.button(
                        "他の企業研究を見る（次の3件）",
                        key=f"{company_key}_more",
                        on_click=show_more_posts,
                        args=(company_index,),
                        width="stretch",
                    )
