from langdetect import detect, DetectorFactory

# Set the seed to ensure consistent results
DetectorFactory.seed = 0

text = ""
language = detect(text)
print(f"The detected language is: {language}")  # Output: The detected language is: fr
