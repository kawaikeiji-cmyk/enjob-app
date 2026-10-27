from datetime import datetime, timezone

import streamlit as st
from supabase import create_client


class CompanyResearchError(RuntimeError):
    """接続情報を含めず、画面に表示できる保存・読み込みエラーです。"""


@st.cache_resource(show_spinner=False)
def get_supabase_client():
    """secrets.tomlの設定で接続します。接続自体だけを再利用します。"""
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_PUBLISHABLE_KEY"],
        )
    except Exception:
        raise CompanyResearchError("Supabaseの接続設定を確認してください。") from None


def save_company_research(company_name, company_url, selections, research):
    """企業研究を1件保存します。各STEPは文字列の配列で送ります。"""
    step_choices = list(selections.values())
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "company_name": company_name,
        "company_url": company_url,
        "step1_choices": list(step_choices[0]),
        "step2_choices": list(step_choices[1]),
        "step3_choices": list(step_choices[2]),
        "research_text": research,
    }
    client = get_supabase_client()
    try:
        # 保存後の行を取得せず、保存の成否だけを確認します。
        client.table("company_research").insert(record, returning="minimal").execute()
    except Exception as error:
        if getattr(error, "code", None) in {"42703", "PGRST204"}:
            raise CompanyResearchError(
                "Supabaseのcompany_researchテーブルに必要な列がありません。列構成を確認してください。"
            ) from None
        raise CompanyResearchError(
            "企業研究を保存できませんでした。Supabaseの接続と登録権限を確認してください。"
        ) from None


def load_company_research(columns):
    """必要な列を、登録順に全件取得します。結果はキャッシュしません。"""
    client = get_supabase_client()
    records = []
    offset = 0
    page_size = 1000
    try:
        while True:
            response = (
                client.table("company_research")
                .select(columns)
                .order("created_at")
                .order("id")
                .range(offset, offset + page_size - 1)
                .execute()
            )
            batch = response.data
            if not batch:
                break
            records.extend(batch)
            offset += len(batch)
    except Exception as error:
        if getattr(error, "code", None) in {"42703", "PGRST204"}:
            raise CompanyResearchError(
                "Supabaseのcompany_researchテーブルに必要な列がありません。列構成を確認してください。"
            ) from None
        raise CompanyResearchError(
            "企業研究を読み込めませんでした。Supabaseの接続と読み取り権限を確認してください。"
        ) from None
    return records
