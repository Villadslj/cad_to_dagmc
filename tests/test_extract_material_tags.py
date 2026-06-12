"""Tests for the automatic material tag extraction from STEP part names."""

import pytest
from cad_to_dagmc.core import (
    extract_material_tag_from_name,
    extract_material_tags_from_names,
)


class TestExtractMaterialTagFromName:
    """Tests for extract_material_tag_from_name helper function."""

    def test_basic_underscore_delimiter(self):
        """ss_watertank → ss"""
        assert extract_material_tag_from_name("ss_watertank") == "ss"

    def test_whitespace_delimiter(self):
        """water tank → water"""
        assert extract_material_tag_from_name("water tank") == "water"

    def test_at_sign_delimiter(self):
        """eurofer@blanket → eurofer"""
        assert extract_material_tag_from_name("eurofer@blanket") == "eurofer"

    def test_multiple_delimiters(self):
        """ss__tank → ss (repeated delimiters)"""
        assert extract_material_tag_from_name("ss__tank") == "ss"

    def test_mixed_delimiters(self):
        """water_coolant_pipe → water"""
        assert extract_material_tag_from_name("water_coolant_pipe") == "water"

    def test_steel_space_delimiter(self):
        """steel tank → steel"""
        assert extract_material_tag_from_name("steel tank") == "steel"

    def test_mat_at_delimiter(self):
        """mat@part1 → mat"""
        assert extract_material_tag_from_name("mat@part1") == "mat"

    def test_leading_whitespace_stripped(self):
        """  ss_tank → ss"""
        assert extract_material_tag_from_name("  ss_tank") == "ss"

    def test_trailing_whitespace_stripped(self):
        """ss_tank   → ss"""
        assert extract_material_tag_from_name("ss_tank   ") == "ss"

    def test_ignore_prefix_with_default_tag(self):
        """IGNORE_bolt with ignore_prefixes=["IGNORE"] and default_tag="vacuum" → vacuum"""
        result = extract_material_tag_from_name(
            "IGNORE_bolt",
            ignore_prefixes=["IGNORE"],
            default_tag="vacuum",
        )
        assert result == "vacuum"

    def test_ignore_prefix_without_default_tag_raises(self):
        """IGNORE_bolt with ignore_prefixes=["IGNORE"] and no default_tag → error"""
        with pytest.raises(ValueError, match="matches ignore prefix"):
            extract_material_tag_from_name(
                "IGNORE_bolt",
                ignore_prefixes=["IGNORE"],
            )

    def test_empty_name_with_default_tag(self):
        """Empty name with default_tag → default_tag"""
        assert extract_material_tag_from_name("", default_tag="vacuum") == "vacuum"

    def test_empty_name_without_default_tag_raises(self):
        """Empty name without default_tag → error"""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_material_tag_from_name("")

    def test_only_delimiters_with_default_tag(self):
        """Name that is only delimiters with default_tag → default_tag"""
        assert extract_material_tag_from_name("___", default_tag="vacuum") == "vacuum"

    def test_only_delimiters_without_default_tag_raises(self):
        """Name that is only delimiters without default_tag → error"""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_material_tag_from_name("___")

    def test_custom_delimiter_pattern(self):
        """Custom delimiter pattern (dash only)"""
        result = extract_material_tag_from_name(
            "steel-tank", delimiter_pattern=r"-"
        )
        assert result == "steel"

    def test_no_delimiter_in_name(self):
        """Single word name → the word itself"""
        assert extract_material_tag_from_name("steel") == "steel"

    def test_ignore_prefix_not_matching(self):
        """Name that doesn't match ignore prefix → normal extraction"""
        result = extract_material_tag_from_name(
            "ss_tank",
            ignore_prefixes=["IGNORE"],
        )
        assert result == "ss"


class TestExtractMaterialTagsFromNames:
    """Tests for extract_material_tags_from_names helper function."""

    def test_multiple_names(self):
        names = ["ss_watertank", "water_coolant", "eurofer@blanket"]
        result = extract_material_tags_from_names(names)
        assert result == ["ss", "water", "eurofer"]

    def test_with_ignore_and_default(self):
        names = ["ss_tank", "IGNORE_bolt", "water_pipe"]
        result = extract_material_tags_from_names(
            names, ignore_prefixes=["IGNORE"], default_tag="vacuum"
        )
        assert result == ["ss", "vacuum", "water"]

    def test_empty_list(self):
        assert extract_material_tags_from_names([]) == []


class TestAddStpFileValidation:
    """Tests for validation in add_stp_file when using extraction mode."""

    def test_both_material_tags_and_extraction_raises(self):
        """Providing both material_tags and extract_material_tags_from_part_names raises."""
        from cad_to_dagmc import CadToDagmc

        model = CadToDagmc()
        with pytest.raises(ValueError, match="Cannot use both"):
            model.add_stp_file(
                filename="dummy.step",
                material_tags=["mat1"],
                extract_material_tags_from_part_names=True,
            )
