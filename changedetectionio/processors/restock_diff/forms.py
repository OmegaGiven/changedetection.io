from wtforms import (
    BooleanField,
    StringField,
    validators,
    FloatField
)
from wtforms.fields.choices import RadioField
from wtforms.fields.form import FormField
from wtforms.form import Form
from flask_babel import lazy_gettext as _l

from changedetectionio.forms import processor_text_json_diff_form, StringListField


class RestockSettingsForm(Form):
    in_stock_processing = RadioField(label=_l('Re-stock detection'), choices=[
        ('in_stock_only', _l("In Stock only (Out Of Stock -> In Stock only)")),
        ('all_changes', _l("Any availability changes")),
        ('off', _l("Off, don't follow availability/restock")),
    ], default="in_stock_only")

    price_change_min = FloatField(_l('Below price to trigger notification'), [validators.Optional()],
                                  render_kw={"placeholder": _l("No limit"), "size": "10"})
    price_change_max = FloatField(_l('Above price to trigger notification'), [validators.Optional()],
                                  render_kw={"placeholder": _l("No limit"), "size": "10"})
    price_change_threshold_percent = FloatField(_l('Threshold in %% for price changes since the original price'), validators=[

        validators.Optional(),
        validators.NumberRange(min=0, max=100, message=_l("Should be between 0 and 100")),
    ], render_kw={"placeholder": "0%", "size": "5"})

    follow_price_changes = BooleanField(_l('Follow price changes'), default=True)
    price_selector = StringField(_l('Price selector'), [validators.Optional()],
                                 render_kw={"placeholder": _l(".price, [itemprop='price']")})
    availability_selector = StringField(_l('Availability selector'), [validators.Optional()],
                                        render_kw={"placeholder": _l(".inventory, .stock, [itemprop='availability']")})
    in_stock_texts = StringListField(_l('Extra in-stock phrases'))
    out_of_stock_texts = StringListField(_l('Extra out-of-stock phrases'))

class processor_settings_form(processor_text_json_diff_form):
    processor_config_restock_diff = FormField(RestockSettingsForm)

    def extra_tab_content(self):
        return _l('Restock & Price Detection')

    def extra_form_content(self):
        output = ""

        if getattr(self, 'watch', None) and getattr(self, 'datastore'):
            for tag_uuid in self.watch.get('tags'):
                tag = self.datastore.data['settings']['application']['tags'].get(tag_uuid, {})
                if tag.get('overrides_watch'):
                    # @todo - Quick and dirty, cant access 'url_for' here because its out of scope somehow
                    output = f"""<p><strong>Note! A Group tag overrides the restock and price detection here.</strong></p><style>#restock-fieldset-price-group {{ opacity: 0.6; }}</style>"""

        output += """
        {% from '_helpers.html' import render_field, render_checkbox_field, render_button %}
        <script>
            $(document).ready(function () {
                toggleOpacity('#processor_config_restock_diff-follow_price_changes', '.price-change-minmax', true);
            });
        </script>

        <fieldset id="restock-fieldset-price-group">
            <div class="pure-control-group">
                <fieldset class="pure-group inline-radio">
                    {{ render_field(form.processor_config_restock_diff.in_stock_processing) }}
                </fieldset>
                <fieldset class="pure-group">
                    {{ render_checkbox_field(form.processor_config_restock_diff.follow_price_changes) }}
                    <span class="pure-form-message-inline">Changes in price should trigger a notification</span>
                </fieldset>
                <fieldset class="pure-group price-change-minmax">
                    {{ render_field(form.processor_config_restock_diff.price_change_min, placeholder=watch.get('restock', {}).get('price')) }}
                    <span class="pure-form-message-inline">Minimum amount, Trigger a change/notification when the price drops <i>below</i> this value.</span>
                </fieldset>
                <fieldset class="pure-group price-change-minmax">
                    {{ render_field(form.processor_config_restock_diff.price_change_max, placeholder=watch.get('restock', {}).get('price')) }}
                    <span class="pure-form-message-inline">Maximum amount, Trigger a change/notification when the price rises <i>above</i> this value.</span>
                </fieldset>
                <fieldset class="pure-group price-change-minmax">
                    {{ render_field(form.processor_config_restock_diff.price_change_threshold_percent) }}
                    <span class="pure-form-message-inline">Price must change more than this % to trigger a change since the first check.</span><br>
                    <span class="pure-form-message-inline">For example, If the product is $1,000 USD originally, <strong>2%</strong> would mean it has to change more than $20 since the first check.</span><br>
                </fieldset>
                <fieldset class="pure-group">
                    {{ render_field(form.processor_config_restock_diff.price_selector) }}
                    <span class="pure-form-message-inline">Optional CSS or XPath selector for the price element on this page.</span>
                </fieldset>
                <fieldset class="pure-group">
                    {{ render_field(form.processor_config_restock_diff.availability_selector) }}
                    <span class="pure-form-message-inline">Optional CSS or XPath selector for the stock/availability element on this page.</span>
                </fieldset>
                <fieldset class="pure-group">
                    {{ render_field(form.processor_config_restock_diff.in_stock_texts, rows=4, placeholder="in stock&#10;available for pickup") }}
                    <span class="pure-form-message-inline">Optional extra phrases that should count as in stock when found in the availability text.</span>
                </fieldset>
                <fieldset class="pure-group">
                    {{ render_field(form.processor_config_restock_diff.out_of_stock_texts, rows=4, placeholder="sold out&#10;backorder") }}
                    <span class="pure-form-message-inline">Optional extra phrases that should count as out of stock when found in the availability text.</span>
                </fieldset>
            </div>
        </fieldset>
        """
        return output
