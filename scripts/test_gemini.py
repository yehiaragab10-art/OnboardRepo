import sys

from google import genai

from onboardrepo.llm import get_gemini_api_key

PROMPT = "Reply with exactly the words inside quotes: " \
"\"Gemini is working\". Do not include any " \
"other text or formatting."


def main() -> int:
    api_key = get_gemini_api_key()

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT,
    )

    text = response.text.strip()

    print("Response:")
    print(text)

    usage = getattr(response, "usage_metadata", None)

    if usage:
        print("\nUsage metadata:")
        print(usage)

    if "Gemini is working" in text:
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())