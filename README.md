# Newman-Practical
Newman – MCP Conversation Flow Tests
This collection contains end-to-end scenario tests for an MCP (Model Context Protocol) server running locally at http://localhost:8765/mcp. It is designed to validate conversational booking workflows — covering happy paths, ambiguous inputs, and error-handling edge cases.
Scenarios
Scenario 1 – Happy Path (Chained, Same Session)
A two-step flow that simulates a successful service booking within a single session:
1a – Oil Change Request: Initiates a booking request for an oil change service.
1b – Confirm Booking (Same Session): Confirms the booking captured in the previous step, validating that session state is correctly maintained across chained requests.

Scenario 2 – Ambiguous Booking
2 – Vague Request (No Service or Time): Submits an underspecified booking request (missing service type and/or time) to verify that the MCP server correctly handles ambiguous or incomplete input.

Scenario 3 – Cancellation Error (Unknown Confirmation ID)
3 – Cancel With Captured (Non-Existent) Confirmation ID: Attempts to cancel a booking using a confirmation ID that does not exist, validating that the server returns an appropriate error response.

Usage
All requests are POST to the local MCP endpoint. Run the collection sequentially (e.g. via Newman or the Collection 
