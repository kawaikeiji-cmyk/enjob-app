"""検索画面の表示・追加表示・再検索を、Supabaseに接続せず確認します。"""

import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from supabase_store import CompanyResearchError


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_options(filename):
    tree = ast.parse((PROJECT_ROOT / filename).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "step_options"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("自己分析Aの選択肢が見つかりません。")


class SearchPageTests(unittest.TestCase):
    def setUp(self):
        self.options = list(read_options("screens/register.py").values())
        self.long_research = "長い企業研究の本文です。\n" * 40 + "全文末尾の確認文字"
        self.rows = []
        for counts in [
            (0, 0, 0),
            (2, 3, 2),
            (3, 3, 3),
            (3, 3, 2),
            (2, 2, 2),
            (1, 1, 1),
            (2, 2, 1),
            (1, 1, 0),
        ]:
            self.add_post("企業A", counts)
        self.add_post("企業B", (3, 3, 2))
        self.add_post("企業C", (0, 0, 0))
        patcher = patch("supabase_store.load_company_research", return_value=self.rows)
        self.loader = patcher.start()
        self.addCleanup(patcher.stop)
        self.app = AppTest.from_file(PROJECT_ROOT / "app.py").run(timeout=30)
        self.app.button[0].click().run(timeout=30)
        self.assertFalse(self.app.exception)

    def add_post(self, company, counts):
        record = {
            "company_name": company,
            "company_url": f"https://example.com/{len(self.rows)}",
            "created_at": "2026-10-29T00:00:00+00:00",
            "research_text": (
                self.long_research if counts == (3, 3, 3) else f"{company}の投稿 {counts}"
            ),
        }
        for step, count in enumerate(counts, start=1):
            options = self.options[step - 1]
            record[f"step{step}_choices"] = list(
                reversed(options[:count] + options[3 : 6 - count])
            )
        self.rows.append(record)

    def search(self):
        for widget in self.app.multiselect:
            widget.set_value(widget.options[:3])
        self.submit()

    def submit(self):
        next(
            button for button in self.app.button if button.label == "企業を検索する"
        ).click().run(timeout=30)
        self.assertFalse(self.app.exception)

    def percentages(self, company_index=0):
        return [
            element.value
            for element in self.app.expander[company_index].markdown
            if element.value.startswith("**投稿者との類似度：")
        ]

    def more(self, company_index=0):
        generation = self.app.session_state["company_search_generation"]
        key = f"search_company_{generation}_{company_index}_more"
        self.app.button(key=key).click().run(timeout=30)
        self.assertFalse(self.app.exception)

    def test_company_headers_and_post_scores_are_separate(self):
        self.search()
        self.assertEqual(
            [expander.label for expander in self.app.expander],
            ["企業A ｜ 企業研究 8件", "企業B ｜ 企業研究 1件", "企業C ｜ 企業研究 1件"],
        )
        self.assertTrue(all("%" not in item.label for item in self.app.expander))
        self.assertFalse(self.app.table)
        self.assertEqual(
            self.percentages(),
            [
                "**投稿者との類似度：100.0%**",
                "**投稿者との類似度：88.9%**",
                "**投稿者との類似度：77.8%**",
            ],
        )
        texts = [element.value for element in self.app.expander[0].text]
        self.assertIn("STEP1：2/3　STEP2：3/3　STEP3：2/3", texts)
        best_post = self.rows[2]
        self.assertIn(best_post["company_url"], texts)
        for step in range(1, 4):
            for choice in best_post[f"step{step}_choices"]:
                self.assertTrue(any(choice in value for value in texts))
        selected_columns = self.loader.call_args.args[0].split(",")
        self.assertIn("company_url", selected_columns)
        self.assertIn("research_text", selected_columns)

    def test_more_posts_are_added_three_at_a_time_without_refetch(self):
        self.search()
        self.more()
        self.assertEqual(len(self.percentages()), 6)
        self.more()
        self.assertEqual(len(self.percentages()), 8)
        self.assertFalse(
            any(button.label.startswith("他の企業研究を見る") for button in self.app.button)
        )
        self.assertEqual(self.loader.call_count, 1)
        self.app.run(timeout=30)
        self.assertEqual(len(self.percentages()), 8)
        self.assertEqual(self.loader.call_count, 1)

    def test_pagination_is_independent_for_each_company(self):
        for counts in [(2, 2, 2), (1, 1, 1), (0, 0, 0), (1, 0, 0)]:
            self.add_post("企業B", counts)
        self.search()
        self.assertEqual(len(self.percentages(1)), 3)
        self.more(0)
        self.assertEqual(len(self.percentages(0)), 6)
        self.assertEqual(len(self.percentages(1)), 3)
        self.more(1)
        self.assertEqual(len(self.percentages(0)), 6)
        self.assertEqual(len(self.percentages(1)), 5)
        self.assertEqual(self.loader.call_count, 1)

    def test_long_text_can_be_opened_without_losing_results(self):
        self.search()
        preview_texts = [element.value for element in self.app.expander[0].text]
        self.assertNotIn(self.long_research, preview_texts)
        self.assertIn(self.long_research[:300] + "…", preview_texts)
        self.app.toggle[0].set_value(True).run(timeout=30)
        self.assertFalse(self.app.exception)
        full_texts = [element.value for element in self.app.expander[0].text]
        self.assertIn(self.long_research, full_texts)
        self.assertEqual(len(self.percentages()), 3)
        self.assertEqual(self.loader.call_count, 1)
        self.app.toggle[0].set_value(False).run(timeout=30)
        self.assertNotIn(
            self.long_research, [element.value for element in self.app.expander[0].text]
        )

    def test_new_search_resets_pagination_and_full_text(self):
        self.search()
        self.more()
        self.app.toggle[0].set_value(True).run(timeout=30)
        self.search()
        self.assertFalse(self.app.error)
        self.assertEqual(len(self.percentages()), 3)
        self.assertFalse(self.app.toggle[0].value)
        self.assertEqual(self.loader.call_count, 2)

    def test_invalid_search_removes_old_results(self):
        self.search()
        for count in range(3):
            self.app.multiselect[1].set_value(self.options[1][:count])
            self.submit()
            self.assertEqual(len(self.app.error), 1)
            self.assertFalse(self.app.expander)
        self.assertEqual(self.loader.call_count, 1)

    def test_empty_data_and_read_error_have_different_messages(self):
        self.loader.side_effect = CompanyResearchError("読み込み確認用のエラー")
        self.search()
        self.assertEqual(len(self.app.error), 1)
        self.assertFalse(self.app.expander)
        self.assertFalse(self.app.info)
        self.loader.side_effect = None
        self.loader.return_value = []
        self.search()
        self.assertFalse(self.app.error)
        self.assertFalse(self.app.expander)
        self.assertEqual(self.app.info[0].value, "まだ企業研究が登録されていません")

    def test_home_navigation_and_registration_screen_are_preserved(self):
        self.search()
        self.app.button[0].click().run(timeout=30)
        self.assertEqual(self.app.header[0].value, "ホーム")
        self.assertNotIn("company_search_results", self.app.session_state)
        self.app.button[1].click().run(timeout=30)
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.text_input), 2)
        self.assertEqual(len(self.app.multiselect), 3)
        self.assertEqual(len(self.app.text_area), 1)
        self.assertEqual(
            list(self.app.table[0].value.columns), ["企業名", "登録日時"]
        )

    def test_options_match_the_registration_screen(self):
        self.assertEqual(
            read_options("screens/register.py"), read_options("screens/search.py")
        )


if __name__ == "__main__":
    unittest.main()
