"""A test feed (a loopback address or a folder) used once on a PC is not the feed every later update check goes to.

strata-nvfp4: "forgotten" and "nothing remembered" mean None here, not upstream's DEFAULT_FEED: this fork never updates
itself from upstream's feed unless one is named, so no feed named falls back to the fork's own updater (strata_cli/fork_update.py)."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from strata_cli import update_cmd
from strata_control import updater


def remembered(root, source):
    state = updater.State(root)
    state.data["feed"] = {"source": source}
    state.save()


class FeedMemoryTest(unittest.TestCase):
    def source(self, stored, **args):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop(update_cmd.ENV_FEED, None)
            remembered(Path(tmp), stored)
            return update_cmd._feed_source(SimpleNamespace(feed=args.get("feed")), Path(tmp))

    def test_a_loopback_test_feed_is_forgotten(self):
        self.assertIsNone(self.source("http://127.0.0.1:18831"))    # None: this fork's own updater, not upstream's feed

    def test_a_local_folder_is_forgotten(self):
        self.assertIsNone(self.source(r"C:\rel\FEED-interim"))
        self.assertIsNone(self.source("/tmp/feed"))

    def test_an_https_mirror_is_kept(self):
        self.assertEqual(self.source("https://mirror.example.com/strata-feed.json"), "https://mirror.example.com/strata-feed.json")

    def test_nothing_remembered_is_the_project_feed(self):
        self.assertIsNone(self.source(None))                        # strata-nvfp4: no feed named is this fork's updater

    def test_a_named_feed_still_wins(self):
        self.assertEqual(self.source("https://a.example/f.json", feed="http://127.0.0.1:1"), "http://127.0.0.1:1")


if __name__ == "__main__":
    unittest.main()
