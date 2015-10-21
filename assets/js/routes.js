import React from 'react';
import { IndexRoute, NotFound, Redirect, Router, Route } from 'react-router';
import { ReduxRouter } from 'redux-router';

import App from './containers/App';
import About from './components/About';
import Maps from './components/Maps';
import Rankings from './components/Rankings';
import Rules from './components/Rules';

const routes = (
  <ReduxRouter>
    <Route path="/" component={App}>
      <Route path="about" component={About}/>
      <Route path="maps" component={Maps}/>
      <Route path="rankings" component={Rankings}/>
      <Route path="rules" component={Rules}/>
      <IndexRoute component={Rankings} />
      <Route path="*" component={NotFound} />
    </Route>
    <Route path="*" component={NotFound} />
  </ReduxRouter>
);

export default routes;
