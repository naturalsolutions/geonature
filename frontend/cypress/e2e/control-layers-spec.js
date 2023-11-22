describe('Testing Leaflet control layers', () => {
  const controlSelector = '.leaflet-control-layers';
  const controlExpandedSelector = `.leaflet-control-layers-expanded`;
  const overlayersTitleSelector = '[data-qa="title-overlay"]';
  beforeEach(()=> {
    cy.geonatureLogin();
    cy.visit('/#/');
  })
  it('should display "overlayers button controler"', () => {
    cy.get(controlSelector).should('be.visible');
    cy.get(controlSelector).trigger('mouseover');
    cy.get(controlExpandedSelector).should('be.visible');
  });
  it('should control "overlayers content"', () => {
    cy.intercept({
      method: 'GET',
      path: '/gn_commons/config',
    }).as("config")
    cy.wait('@config').then(({response}) => {
      expect(response.statusCode).to.eq(200)
      cy.get(overlayersTitleSelector).its("length").then((size)=>{
        expect(response.body.MAPCONFIG.REF_LAYERS).to.have.length(size)
      })
      
    })
  });
});
