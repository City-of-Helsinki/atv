import { Page, expect, test } from '@playwright/test';


test.describe("Api schema", () => {
    test('schema test', async ({ request }) => {
        const response = await request.get(`/v1/schema/?format=json`);
        expect(response .ok()).toBeTruthy();

        // check schema keys and values
        response.json().then((data) => {
            expect(data).not.toBeNull();

            expect(data).toHaveProperty("openapi");
            expect(data).toHaveProperty("info");
            expect(data).toHaveProperty("info.title");
            expect(data).toHaveProperty("info.version");
            expect(data).toHaveProperty("paths");


            expect(data.openapi).toEqual("3.0.3");
            expect(data.info.title).toEqual(" Asiointitietovaranto ");
        });
      
      });

})
