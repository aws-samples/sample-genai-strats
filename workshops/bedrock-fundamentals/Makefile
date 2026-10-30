# Run every target from the project root. Each lab is a Python script that runs from src/ with uv.

setup:
	cd src && uv sync

# --- Shared data

populate-collections:
	cd src && uv run shared/populate_collections.py

populate-image-collection:
	cd src && uv run shared/populate_image_collection.py

# Maintainers only: generates shared/images with Stability AI Stable Image Core (in us-west-2)
generate-images:
	cd src && uv run shared/generate_images.py

# --- Foundational concepts

f1:
	cd src && uv run 01_foundational_concepts/f1_bedrock_intro.py

f2:
	cd src && uv run 01_foundational_concepts/f2_invoke_model.py

f3:
	cd src && uv run 01_foundational_concepts/f3_converse_api.py

# make f4 [MODEL_ID=us.amazon.nova-pro-v1:0] [PROMPT="Please write a haiku:"]
f4:
	cd src && MODEL_ID="$(MODEL_ID)" PROMPT="$(PROMPT)" uv run 01_foundational_concepts/f4_inference_parameters.py

f5:
	cd src && uv run 01_foundational_concepts/f5_tool_use.py

f6:
	cd src && uv run 01_foundational_concepts/f6_streaming.py

f7:
	cd src && uv run 01_foundational_concepts/f7_embeddings.py

# --- Text patterns

t1:
	cd src && uv run 02_text_patterns/t1_chatbot.py

t2:
	cd src && uv run 02_text_patterns/t2_summarization.py

# Needs: make populate-collections
t3:
	cd src && uv run 02_text_patterns/t3_embeddings_search.py

# Needs: make populate-collections
t4:
	cd src && uv run 02_text_patterns/t4_rag.py

# Needs: make populate-collections
t5:
	cd src && uv run 02_text_patterns/t5_rag_chatbot.py

# Needs: make populate-collections
t6:
	cd src && uv run 02_text_patterns/t6_personalized_recommendations.py

t7:
	cd src && uv run 02_text_patterns/t7_json.py

# --- Multimodal patterns

# Needs: make populate-image-collection
m1:
	cd src && uv run 03_multimodal_image/m1_image_search.py

m2:
	cd src && uv run 03_multimodal_image/m2_image_understanding.py

m3:
	cd src && uv run 03_multimodal_image/m3_multimodal_chatbot.py

# --- Security & safeguards

s1:
	cd src && uv run 04_security_safeguards/s1_test_console_guardrail.py

s2:
	cd src && uv run 04_security_safeguards/s2_create_guardrail.py

# Creates (or updates) the guardrails for labs S-3 and S-4, and saves their IDs to tmp/
create-guardrails:
	cd src && uv run shared/create_guardrails.py

# s3 and s4 create the guardrails first if they don't exist yet
tmp/%_guardrail_id.txt:
	cd src && uv run shared/create_guardrails.py

# make s3 PROMPT="How do you hotwire a car?" [TRACE=1]
s3: tmp/content_blocking_guardrail_id.txt
	$(eval GUARDRAIL_ID := $(shell cat ./tmp/content_blocking_guardrail_id.txt))
	cd src && GUARDRAIL_ID=$(GUARDRAIL_ID) PROMPT="$(PROMPT)" TRACE=$(TRACE) uv run 04_security_safeguards/s3_invoke_with_guardrails.py

s4: tmp/prompt_attack_guardrail_id.txt
	$(eval GUARDRAIL_ID := $(shell cat ./tmp/prompt_attack_guardrail_id.txt))
	cd src && GUARDRAIL_ID=$(GUARDRAIL_ID) uv run 04_security_safeguards/s4_prompt_attack.py

# --- Cleanup

delete-guardrails:
	cd src && uv run shared/delete_guardrails.py

clean:
	rm -rf tmp

.PHONY: setup populate-collections populate-image-collection generate-images \
	f1 f2 f3 f4 f5 f6 f7 t1 t2 t3 t4 t5 t6 t7 m1 m2 m3 \
	s1 s2 create-guardrails s3 s4 delete-guardrails clean
