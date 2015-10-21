import React from 'react';
import { IndexRedirect, IndexRoute, NotFound, Redirect, Router,
         Route } from 'react-router';
import { ReduxRouter } from 'redux-router';

import App from './containers/App';
import About from './components/About';
import Hypermeet2015 from './components/Hypermeet2015';
import Maps from './components/Maps';
import Matches from './components/Matches';
import Rankings from './containers/Rankings';
import RankingTable from './components/RankingTable';
import Rules from './components/Rules';

const routes = (
  <ReduxRouter>
    <Route path="/" component={App}>
      <Route path="about" component={About} />
      <Route path="hypermeet2015" component={Hypermeet2015} />
      <Route path="maps" component={Maps} />
      <Route path="rankings" component={Rankings}>
        <Route path="matches" component={Matches} />
        <Route path="players" component={RankingTable} />
        <IndexRedirect to="players" />
      </Route>
      <Route path="rules" component={Rules} />
      <IndexRedirect to="rankings" />
      <Route path="*" component={NotFound} />
    </Route>
    <Route path="*" component={NotFound} />
  </ReduxRouter>
);

export default routes;
