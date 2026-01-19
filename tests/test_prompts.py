from app.core.prompts import get_prompt_variants


def test_get_prompt_variants_unique_ids():
    variants = get_prompt_variants()
    ids = [variant.id for variant in variants]
    assert len(variants) >= 5
    assert len(set(ids)) == len(ids)


def test_prompt_variants_have_system_prompts():
    variants = get_prompt_variants()
    for variant in variants:
        assert variant.system_prompt.strip()
