import pytest

from project.ecfg import ECFG
from project.rsm import RSM


@pytest.mark.parametrize(
    """ecfg_text""",
    (
        """
        """,
        """
        S -> $
        """,
        """
        S -> (a S b S) f*
        B -> B | (B C)
        C -> (A* B*) | (A* B*)
        """,
    ),
)
def test_rsm_minimize(ecfg_text):
    ecfg = ECFG.from_text(ecfg_text)
    rsm = RSM.from_ecfg(ecfg).minimize()
    minimized_rsm = rsm.minimize()
    assert all(
        map(
            lambda x: rsm.boxes[x].is_equivalent_to(minimized_rsm.boxes[x]),
            minimized_rsm.boxes,
        )
    )
