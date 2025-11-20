# 💰 Project Cost Estimate (Weekly Operation)

This document provides an estimated operational cost for running the **AI-Powered Novel-to-Video Generator** on a weekly basis.

> **Note**: Prices are based on public pricing as of late 2024. Actual costs may vary based on region and specific model versions.
> **Exchange Rate Used**: $1 USD ≈ ₹85 INR.

---

## 📊 Cost Scenarios Overview

We assume a weekly production of:
*   **3 Short Videos** (60 seconds each, ~10 scenes)
*   **1 Full-Length Video** (5 minutes, ~50 scenes)
*   **Total Assets**: 80 Images, ~8,000 Characters (TTS), ~20k Tokens (LLM)

| Scenario | Weekly Cost | Monthly Cost | Quality Level |
| :--- | :--- | :--- | :--- |
| **🟢 Budget** | **$0.00 (₹0)** | **$0.00 - $2.00 (₹0 - ₹170)** | MVP / Testing |
| **🟡 Standard** | **~$3.50 (₹300)** | **~$15.00 (₹1,275)** | Professional |
| **🔵 Hybrid (Best Value)** | **~$11.50 (₹980)** | **~$46.00 (₹3,900)** | **Premium Voice + Pro Visuals** |
| **🔴 Premium** | **~$25.00+ (₹2,125+)** | **~$100.00+ (₹8,500+)** | Cinema / Broadcast |

---

## 1. 🟢 Budget Scenario (Lowest Cost)

**Goal**: Minimize spend using free tiers and cheaper models.

*   **LLM**: **Gemini 1.5 Flash** (Free tier or very cheap)
*   **Images**: **Stable Diffusion XL (Local)** or **Pollinations.ai** (Free APIs)
*   **Voice**: **Google Cloud TTS (Standard)** (Free tier covers usage)
*   **Music**: **Royalty-Free Library** (Free)

| Resource | Cost Calculation | Weekly Total |
| :--- | :--- | :--- |
| **Images** | Local GPU / Free API | **$0.00 (₹0)** |
| **Voice** | Free Tier (1M chars) | **$0.00 (₹0)** |
| **LLM** | Free Tier / Flash | **$0.00 (₹0)** |
| **Total** | | **$0.00 (₹0)** |

---

## 2. 🟡 Standard Scenario (Balanced)

**Goal**: Great quality using Google's ecosystem (Current Implementation).

*   **LLM**: **Gemini 1.5 Pro** (Better reasoning for scenes)
*   **Images**: **Vertex AI Imagen 3** (High consistency)
*   **Voice**: **Google Cloud TTS (Neural2)** (Natural sounding)
*   **Music**: **Royalty-Free Library**

| Resource | Cost Calculation | Weekly Total |
| :--- | :--- | :--- |
| **Images** | 80 images * $0.04 (₹3.40) | **$3.20 (₹272)** |
| **Voice** | Free Tier (mostly) | **$0.13 (₹11)** |
| **LLM** | Pro Pricing | **$0.10 (₹8.50)** |
| **Total** | | **~$3.43 (₹292)** |

---

## 3. 🔵 Hybrid Scenario (Smart Spender) 🏆

**Goal**: "Premium" feel where it counts (Voice) while saving on others.

*   **LLM**: **Gemini 1.5 Pro** (Standard) - Good enough for scripts.
*   **Images**: **Vertex AI Imagen 3** (Standard) - Excellent quality/price ratio.
*   **Voice**: **ElevenLabs** (Premium) - Use for **Narrator only** (50% of text).
*   **Voice**: **Google Neural2** (Standard) - Use for **Characters** (50% of text).

| Resource | Cost Calculation | Weekly Total |
| :--- | :--- | :--- |
| **Images** | 80 images * $0.04 (₹3.40) | **$3.20 (₹272)** |
| **Voice (Premium)** | 4,000 chars * $0.002 (ElevenLabs) | **$8.00 (₹680)** |
| **Voice (Standard)** | 4,000 chars (Free Tier) | **$0.00 (₹0)** |
| **LLM** | Pro Pricing | **$0.10 (₹8.50)** |
| **Total** | | **~$11.30 (₹960)** |

---

## 4. 🔴 Premium Scenario (Highest Quality)

**Goal**: Top-tier aesthetics and human-like voice everywhere.

*   **LLM**: **GPT-4o** (Top-tier creative writing)
*   **Images**: **Midjourney v6 / DALL-E 3** (Best artistic control)
*   **Voice**: **ElevenLabs** (All voices)
*   **Music**: **Suno / Udio** (AI Generated Music)

| Resource | Cost Calculation | Weekly Total |
| :--- | :--- | :--- |
| **Images** | 80 images * ~$0.08 (₹6.80) | **$6.40 (₹544)** |
| **Voice** | 8,000 chars * $0.002 (₹0.17) | **$16.00 (₹1,360)** |
| **LLM** | GPT-4o Pricing | **$0.50 (₹42)** |
| **Music** | AI Generation Subscription | **$2.50 (₹212)** |
| **Total** | | **~$25.40 (₹2,158)** |

---

## 💡 Recommendation

**Start with Standard (🟡)**.
If you want to upgrade, move to **Hybrid (🔵)** by integrating ElevenLabs just for the narrator. This gives you the "Premium" sound for only ~$8/week extra, which is the highest ROI upgrade you can make.
