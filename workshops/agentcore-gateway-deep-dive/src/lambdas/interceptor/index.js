export const handler = async (event) => {
  console.log("incoming event", JSON.stringify(event, null, 2));

  let response;

  if (event.mcp.gatewayResponse) {
    // ── RESPONSE interception ─────────────────────────────────────────────────
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

    // Pass-through: no changes to the response

  } else if (event.mcp.gatewayRequest) {
    // ── REQUEST interception ──────────────────────────────────────────────────
    console.log("> gateway request intercepted");
    response = {
      interceptorOutputVersion: "1.0",
      mcp: {
        transformedGatewayRequest: {
          body: event.mcp.gatewayRequest.body,
        },
      },
    };

    // Pass-through: no changes to the request
  }

  console.log("interceptor response", JSON.stringify(response, null, 2));
  return response;
};
