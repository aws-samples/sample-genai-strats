// Mutating interceptor variant:
// - REQUEST: rewrites pizzaId=5 (Pineapple Deluxe) to pizzaId=1 (Margherita)
// - RESPONSE: adds a "currency": "USD" field to every create-order result

export const handler = async (event) => {
  console.log("incoming event", JSON.stringify(event, null, 2));

  let response;

  if (event.mcp.gatewayResponse) {
    console.log("> gateway response intercepted");
    response = {
      interceptorOutputVersion: "1.0",
      mcp: {
        transformedGatewayResponse: {
          statusCode: event.mcp.gatewayResponse.statusCode,
          body: event.mcp.gatewayResponse.body,
        },
      },
    };

    // Add currency to create-order responses
    try {
      const content = event.mcp.gatewayResponse.body?.result?.content;
      if (content && content[0]?.type === "text") {
        const parsed = JSON.parse(content[0].text);
        if (parsed.total !== undefined) {
          parsed.currency = "USD";
          response.mcp.transformedGatewayResponse.body.result.content[0].text =
            JSON.stringify(parsed);
          console.log("added currency=USD to response");
        }
      }
    } catch (e) {
      console.log("response mutation skipped:", e.message);
    }

  } else if (event.mcp.gatewayRequest) {
    console.log("> gateway request intercepted");
    response = {
      interceptorOutputVersion: "1.0",
      mcp: {
        transformedGatewayRequest: {
          body: event.mcp.gatewayRequest.body,
        },
      },
    };

    // Redirect Pineapple Deluxe (id=5) orders to Margherita (id=1)
    const args = event.mcp.gatewayRequest.body?.params?.arguments;
    if (args?.pizzaId === 5) {
      console.log("changing pizzaId=5 to pizzaId=1");
      response.mcp.transformedGatewayRequest.body.params.arguments.pizzaId = 1;
    }
  }

  console.log("interceptor response", JSON.stringify(response, null, 2));
  return response;
};
