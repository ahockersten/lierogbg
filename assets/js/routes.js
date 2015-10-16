import React from 'react';
import { IndexRoute, NotFound, Redirect, Router, Route } from 'react-router';
import { ReduxRouter } from 'redux-router';

import App from './containers/App';

const routes = (
  <ReduxRouter>
    <Redirect from="/" to="/app" />
    <Route path="/app" component={App}>
      <IndexRoute component={App} />
      <Route path="*" component={NotFound} />
    </Route>,
    <Route path="*" component={NotFound} />
  </ReduxRouter>
);

export default routes;
