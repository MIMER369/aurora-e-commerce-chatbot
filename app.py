import streamlit as st
import re
import difflib

st.set_page_config(page_title="Aurora | AI Shopping Assistant", page_icon="🛍️", layout="centered")

# ---------------------------------------------------------------------------
# Royal Green theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #06281c 0%, #0b3d2e 45%, #0f4c3a 100%);
}
section[data-testid="stSidebar"] {
    background: #041a12;
    border-right: 1px solid #d4af37;
}
h1, h2, h3 {
    color: #d4af37 !important;
    font-family: 'Georgia', serif;
}
p, span, label, .stMarkdown {
    color: #eef7f1;
}
.aurora-header {
    text-align: center;
    padding: 18px 10px 8px 10px;
}
.aurora-header .crown {
    font-size: 40px;
}
.aurora-header h1 {
    margin: 4px 0 0 0;
    letter-spacing: 2px;
}
.aurora-header p {
    color: #b7d9c7;
    font-size: 14px;
    margin-top: 2px;
}
div[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 4px 6px;
    margin-bottom: 6px;
}
.stChatInput textarea {
    background-color: #0f2e22 !important;
    color: #ffffff !important;
    border: 1px solid #d4af37 !important;
    border-radius: 12px !important;
}
button[kind="primary"] {
    background-color: #d4af37 !important;
    color: #05271b !important;
    border: none !important;
}
hr { border-color: #d4af37; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aurora-header">
    <div class="crown">👑🛍️</div>
    <h1>AURORA</h1>
    <p>Your royal green e-commerce shopping assistant</p>
</div>
<hr>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Knowledge base (covers the ~70% most repeated e-commerce questions)
# ---------------------------------------------------------------------------
FAQS = [
    {"q": ["hi", "hello", "hey", "good morning", "good evening"],
     "a": "Hello! 👋 I'm Aurora, your shopping assistant. Ask me about orders, shipping, returns, payments or anything else about your purchase."},
    {"q": ["thanks", "thank you", "thank u", "appreciate it"],
     "a": "You're very welcome! Is there anything else I can help you with today? 😊"},
    {"q": ["bye", "goodbye", "see you", "talk later"],
     "a": "Thanks for stopping by! Have a wonderful day, and happy shopping! 🛍️"},
    {"q": ["where is my order", "track my order", "order status", "track order", "order tracking"],
     "a": "You can track your order anytime from **My Orders** in your account. Once shipped, you'll receive a tracking link by email/SMS with real-time updates."},
    {"q": ["how long does shipping take", "shipping time", "delivery time", "when will i get my order"],
     "a": "Standard delivery usually takes 3-7 business days, and express delivery takes 1-2 business days, depending on your location."},
    {"q": ["shipping cost", "delivery charges", "shipping fee", "how much is shipping"],
     "a": "Shipping is free on orders over $50. Orders below that have a flat shipping fee of $4.99."},
    {"q": ["international shipping", "do you ship internationally", "ship to other countries"],
     "a": "Yes! We ship to most countries worldwide. International delivery typically takes 7-15 business days, and customs fees may apply depending on your country."},
    {"q": ["return policy", "how do i return an item", "can i return this", "return item"],
     "a": "We offer a 30-day hassle-free return policy. Items must be unused and in original packaging. Start a return from **My Orders > Return Item**."},
    {"q": ["refund status", "when will i get my refund", "refund time", "refund policy"],
     "a": "Refunds are processed within 5-7 business days after we receive your returned item, and credited to your original payment method."},
    {"q": ["exchange item", "can i exchange", "size exchange"],
     "a": "Absolutely, you can request an exchange for a different size or color within 30 days from **My Orders > Exchange Item**."},
    {"q": ["cancel my order", "how to cancel order", "cancel order"],
     "a": "You can cancel your order within 1 hour of placing it from **My Orders > Cancel Order**. After that, please contact support and we'll do our best to help."},
    {"q": ["change my order", "modify order", "edit order address"],
     "a": "Order details can be modified within 1 hour of purchase from **My Orders > Edit Order**. After that, please reach out to our support team."},
    {"q": ["payment methods", "how can i pay", "what payments do you accept"],
     "a": "We accept all major credit/debit cards, PayPal, Apple Pay, Google Pay, and popular local payment options at checkout."},
    {"q": ["is my payment secure", "payment security", "is it safe to pay here"],
     "a": "Yes, all payments are encrypted and processed through secure, PCI-compliant payment gateways. We never store your full card details."},
    {"q": ["discount code", "coupon code", "promo code", "do you have any offers"],
     "a": "You can apply your coupon code at checkout in the **Promo Code** box. Subscribe to our newsletter for exclusive seasonal discounts!"},
    {"q": ["out of stock", "restock", "when will this be back in stock"],
     "a": "Click **Notify Me** on the product page and we'll email you the moment it's back in stock."},
    {"q": ["product sizing", "size guide", "what size should i order"],
     "a": "Check the **Size Guide** link on every product page for detailed measurements to find your perfect fit."},
    {"q": ["is this product authentic", "product warranty", "warranty"],
     "a": "All our products are 100% authentic and sourced directly from brands or authorized distributors. Most items include a manufacturer warranty - check the product page for details."},
    {"q": ["damaged item", "defective product", "wrong item received", "missing item in order"],
     "a": "So sorry about that! Please contact support with your order number and a photo, and we'll arrange a free replacement or refund right away."},
    {"q": ["create an account", "sign up", "how to register"],
     "a": "Tap **Sign Up** at the top of the page and enter your email and a password to create your free account in seconds."},
    {"q": ["forgot password", "reset password", "cant login"],
     "a": "Click **Forgot Password** on the login page and we'll email you a secure link to reset it."},
    {"q": ["delete my account", "close my account"],
     "a": "You can request account deletion from **Account Settings > Privacy > Delete Account**, or contact support for help."},
    {"q": ["contact support", "customer service", "talk to a human", "phone number"],
     "a": "Our support team is available 24/7 via live chat, or email support@aurora-shop.com. We usually reply within a few hours."},
    {"q": ["gift card", "buy a gift card"],
     "a": "Gift cards are available in the **Gift Cards** section and can be delivered instantly by email in any amount you choose."},
    {"q": ["loyalty program", "reward points", "membership benefits"],
     "a": "Join Aurora Rewards to earn points on every purchase, redeemable for discounts, free shipping and exclusive early access to sales."},
    {"q": ["price match", "found it cheaper elsewhere"],
     "a": "We offer price matching within 7 days of purchase for identical items from select major retailers. Contact support with a link to the lower price."},
    {"q": ["eco friendly packaging", "sustainability", "is packaging recyclable"],
     "a": "We use recyclable and minimal packaging wherever possible, as part of our commitment to sustainability."},
    {"q": ["bulk order", "wholesale", "business order"],
     "a": "For bulk or wholesale inquiries, please email business@aurora-shop.com and our team will get back to you with special pricing."},
]

STOPWORDS = {"a","an","the","is","are","do","does","did","i","my","me","to","for","of","in","on","can","you","your","it","this","that","how","what","when","where","please","hi","hello"}

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).strip()

def score_variant(user_norm: str, user_words: set, variant: str) -> float:
    v_norm = normalize(variant)
    v_words = set(w for w in v_norm.split() if w)
    if not v_words:
        return 0.0
    if len(v_words) <= 2 and v_words.issubset(user_words):
        return 1.0
    overlap = len(user_words & v_words) / max(len(v_words), 1)
    ratio = difflib.SequenceMatcher(None, user_norm, v_norm).ratio()
    return max(overlap * 0.9, ratio)

def best_match(user_input: str):
    user_norm = normalize(user_input)
    user_words = set(w for w in user_norm.split() if w and w not in STOPWORDS) or set(user_norm.split())
    best_score, best_answer, best_q = 0.0, None, None
    for entry in FAQS:
        for variant in entry["q"]:
            s = score_variant(user_norm, user_words, variant)
            if s > best_score:
                best_score, best_answer, best_q = s, entry["a"], variant
    return best_score, best_answer, best_q

def generate_answer(user_input: str, api_key: str | None):
    score, answer, matched_q = best_match(user_input)

    if score >= 0.55:
        return answer

    # Not a confident FAQ match - try optional AI fallback (RAG-lite: FAQs as context)
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            context_snippets = []
            scored = []
            user_norm = normalize(user_input)
            user_words = set(user_norm.split())
            for entry in FAQS:
                s = max(score_variant(user_norm, user_words, v) for v in entry["q"])
                scored.append((s, entry["a"]))
            scored.sort(key=lambda x: x[0], reverse=True)
            context_snippets = [a for s, a in scored[:3]]
            context_text = "\n".join(f"- {c}" for c in context_snippets)

            system_prompt = (
                "You are Aurora, a friendly and helpful e-commerce shopping assistant. "
                "Use the store knowledge below if relevant, otherwise answer naturally and helpfully. "
                "Keep answers concise and warm.\n\nStore knowledge:\n" + context_text
            )
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.6,
                max_tokens=300,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"I hit a small snag reaching the AI service ({e}). Here's my best guess based on what I know: {answer or 'Could you rephrase your question, or contact support@aurora-shop.com?'}"

    if answer:
        return f"I don't have an exact answer for that, but here's something related that might help:\n\n{answer}\n\nYou can also reach our support team at support@aurora-shop.com."
    return ("I don't have an exact answer for that yet. You can reach our support team anytime at "
            "support@aurora-shop.com, or try rephrasing your question.")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👑 Aurora Settings")
    st.write("Aurora instantly answers the most common shopping questions for free, no setup needed.")
    api_key = st.text_input(
        "Optional: your own OpenAI API key (for open-ended AI answers)",
        type="password",
        help="Only used in your browser session. Never stored or shared. Get one at platform.openai.com.",
    )
    st.caption("Leave blank to just use Aurora's built-in shopping FAQ knowledge.")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Chat state & UI
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! 👋 I'm **Aurora**, your e-commerce shopping assistant. Ask me about orders, shipping, returns, payments and more!"}
    ]

for msg in st.session_state.messages:
    avatar = "👑" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Aurora anything about your order...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    reply = generate_answer(user_input, api_key.strip() if api_key else None)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="👑"):
        st.markdown(reply)
