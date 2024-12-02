from metagpt.roles.role import Role
from ffai.actions.simple_wirte_review import SimpleWriteReview
from ffai.actions.simple_write_test import SimpleWriteTest

class SimpleReviewer(Role):
    name: str = "Charlie"
    profile: str = "SimpleReviewer"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SimpleWriteReview])
        self._watch([SimpleWriteTest])
