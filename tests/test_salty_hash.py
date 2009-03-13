from melk.util.hash import salty_hash, salty_hash_matches

def test_salty_hash_simple():
    i = "some_string"
    j = "some_other_string"
    hi = salty_hash(i)
    hj = salty_hash(j)
    
    assert hi != i and hj != j and hi != hj
    
    assert salty_hash_matches(i, hi)
    assert salty_hash_matches(j, hj)
    assert not salty_hash_matches(i, hj)
    assert not salty_hash_matches(j, hi)
