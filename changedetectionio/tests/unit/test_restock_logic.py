#!/usr/bin/env python3

# run from dir above changedetectionio/ dir
# python3 -m unittest changedetectionio.tests.unit.test_restock_logic

import unittest
import os

import changedetectionio.processors.restock_diff.processor as restock_diff

# mostly
class TestDiffBuilder(unittest.TestCase):

    def test_logic(self):
        assert restock_diff.is_between(number=10, lower=9, upper=11) == True, "Between 9 and 11"
        assert restock_diff.is_between(number=10, lower=0, upper=11) == True, "Between 9 and 11"
        assert restock_diff.is_between(number=10, lower=None, upper=11) == True, "Between None and 11"
        assert not restock_diff.is_between(number=12, lower=None, upper=11) == True, "12 is not between None and 11"

    def test_restock_selector_extract_text_css(self):
        html = '<div class="big-price">$199.99</div><div class="inventory">Sold Out</div>'
        assert restock_diff._selector_extract_text(html, '.big-price') == '$199.99'
        assert restock_diff._selector_extract_text(html, '.inventory') == 'Sold Out'

    def test_restock_selector_extract_attribute(self):
        html = '<meta class="product-price" content="199.99"><div class="inventory" data-state="sold out">Sold Out</div>'
        assert restock_diff._selector_extract_text(html, '.product-price', attribute='content') == '199.99'
        assert restock_diff._selector_extract_text(html, '.inventory', attribute='data-state') == 'sold out'

    def test_restock_multiple_selectors_first_match(self):
        html = '<div class="fallback-price">$149.99</div>'
        match = restock_diff._extract_first_matching_selector(html, ['.missing', '.fallback-price'])
        assert match['selector'] == '.fallback-price'
        assert match['value'] == '$149.99'

    def test_restock_custom_availability_keywords(self):
        assert restock_diff._availability_to_instock_state(
            'SOLD OUT',
            out_of_stock_texts=['sold out']
        ) is False
        assert restock_diff._availability_to_instock_state(
            'Available for pickup today',
            in_stock_texts=['available for pickup']
        ) is True

    def test_page_text_custom_phrase_fallback(self):
        restock = restock_diff._apply_page_text_phrase_fallback(
            {},
            '<html><body><div>Ships tomorrow - sold out online</div></body></html>',
            {'page_text_custom_phrase_fallback': True, 'out_of_stock_texts': ['sold out online']}
        )
        assert restock.get('in_stock') is False

if __name__ == '__main__':
    unittest.main()
