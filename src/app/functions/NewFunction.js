
exports.main = async (context, sendResponse) => {
  const body = context.body;
  
  // HubSpot Deal Stage Change event
  // We want to see if the property "dealstage" changed to "closedwon"
  if (body) {
    for (const event of body) {
      if (
        event.subscriptionType === 'deal.propertyChange' &&
        event.propertyName === 'dealstage' &&
        event.propertyValue === 'closedwon'
      ) {
        console.log(`Deal Won Detected: ${event.objectId}`);
        
        // Next step: Call Hubspot API to get deal details
        // Then call Jobber API
      }
    }
  }

  sendResponse({ body: { message: 'Webhook received' }, statusCode: 200 });
};
