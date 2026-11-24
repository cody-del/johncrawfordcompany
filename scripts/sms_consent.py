"""The optional SMS consent block shared by every lead form (A2P 10DLC).

The wording follows the Shenandoah Shutters forms, whose carrier campaign was approved.
docs/a2p-campaign-package.md quotes it, and tests/sms-consent.test.mjs keeps the two in step,
so change both together. Neither box is checked or required; app.js sends each choice as
smsTransactionalOptIn / smsMarketingOptIn and netlify/lib/lead.mjs tags and notes it.
"""

LEGAL_NAME = 'John Crawford Company'


def sms_consent(prefix):
    """The SMS fieldset for one form; prefix keeps its ids unique on the page."""
    disclosure = f'{prefix}-sms-disclosure'
    return f'''<fieldset class="sms-consent">
        <legend>SMS updates (optional)</legend>
        <label class="sms-consent-option" for="{prefix}-sms-transactional"><input id="{prefix}-sms-transactional" name="sms_transactional" type="checkbox" value="yes" aria-describedby="{disclosure}"><span>I agree to receive service texts from <strong>{LEGAL_NAME}</strong> about consultations, appointments, estimates, installations, repairs, and customer support.</span></label>
        <label class="sms-consent-option" for="{prefix}-sms-marketing"><input id="{prefix}-sms-marketing" name="sms_marketing" type="checkbox" value="yes" aria-describedby="{disclosure}"><span>I agree to receive promotional texts from <strong>{LEGAL_NAME}</strong> about offers and product news.</span></label>
        <p class="sms-disclosure" id="{disclosure}">For either option: Message frequency varies. Message and data rates may apply. Reply <strong>STOP</strong> to opt out or <strong>HELP</strong> for help. Consent is not a condition of purchase.</p>
        <p class="sms-policy-links"><a href="/privacy/">Privacy Policy</a> · <a href="/terms/">Terms</a> · <a href="/sms-consent/">SMS details</a></p>
      </fieldset>'''
