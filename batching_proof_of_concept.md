# AI Shipment Tracking Pipeline - Batching Proof of Concept

## **Project Overview**
The objective of this project is to test and validate the ability to send **up to 20,000 shipments** in a single API request to OpenAI's **GPT-4o model** using its **maximum context length of 128,000 tokens**. The pipeline will process shipment scan histories, generate structured AI responses, and store the results in **MongoDB** for analysis.

---

## **Scope of Work**

### **1. Define the JSON Schema for AI Responses**
- AI should return **structured numerical responses** for shipment statuses.
- Schema must include:
  - **`shipment_id`**: Unique shipment identifier.
  - **`progress`**: Numeric code representing shipment progress.
  - **`sub_status`**: Numeric code for additional details.
  - **`final_status`**: Numeric code for the shipment's last known state.

### **2. Test the JSON Schema with Sample Data**
- Conduct a **small-scale test batch (500 shipments)**.
- Validate AI outputs for **correct numerical mapping**.
- Ensure schema consistency across responses.

### **3. Build the Shipment Database in MongoDB**
- Aggregate **scan groups from 141+ collections** into a structured dataset.
- Optimize for **fast retrieval and indexing** on `shipment_id`.
- Ensure **data integrity and consistency** across multiple sources.

### **4. Enhance Developer Prompt with Smart Scans**
- Improve AI reasoning by refining **shipment tracking scenarios**.
- Introduce **classification rules** for handling:
  - Failed deliveries
  - Customs delays
  - Multiple failed collection attempts
  - Out for delivery scenarios

### **5. Create the Prompt Batch Generator**
- Extract **20,000 shipments from MongoDB**.
- Structure the data into a **JSON batch** optimized for OpenAI.
- Implement **token estimation** to ensure requests stay within the **128,000-token limit**.

### **6. Update the Main Processing Script**
- Use the **prompt generator** to format AI requests.
- Implement a **MongoDB handler** to:
  - Insert AI responses into a **dedicated collection**.
  - Ensure **shipment ID mapping** for accurate tracking.
- Store **token usage per request** for cost tracking.

### **7. Validate the Batch Processing Capability**
- Run a **full-scale test with 20,000 shipments** in a **single API request**.
- Measure **token usage per batch**.
- Validate **accuracy and completeness** of AI responses.

### **8. Analyze and Optimize Performance**
- Evaluate:
  - **API response times**
  - **Cost per request**
  - **Token efficiency**
- Adjust **batch sizes** if needed to ensure reliability.

---

## **Deliverables**
- ✅ **Structured AI response schema** with numerical status codes.
- ✅ **MongoDB database** containing shipment data and AI-generated statuses.
- ✅ **Batch processing function** capable of handling **20,000 shipments per request**.
- ✅ **Full-scale validation test** proving **GPT-4o can process large-scale shipments in one API call**.
- ✅ **Token usage reports** for cost efficiency analysis.

---

## **Implementation Plan**
| Step | Task | Status |
|------|------|--------|
| 1 | Define the JSON Schema | ☐ Not Started |
| 2 | Test Schema with Sample Data | ☐ Not Started |
| 3 | Build MongoDB Shipment Dataset | ☐ Not Started |
| 4 | Enhance Developer Prompt | ☐ Not Started |
| 5 | Implement Prompt Batch Generator | ☐ Not Started |
| 6 | Update Main Processing Script | ☐ Not Started |
| 7 | Run Full-Scale Batch Test | ☐ Not Started |
| 8 | Analyze and Optimize Performance | ☐ Not Started |

---

## **Next Steps**
1. **Finalize the JSON schema.**
2. **Conduct an initial AI test with 500 shipments.**
3. **Build the MongoDB shipment dataset.**
4. **Implement the batch processing function.**
5. **Perform a full-scale test with 20,000 shipments.**
6. **Evaluate results and refine the process.**

This proof of concept will determine whether **GPT-4o can reliably process large shipment batches** within a **single API request**, while maintaining **structured and accurate outputs**.

---

## **License**
This project is intended for **internal testing and development**.
