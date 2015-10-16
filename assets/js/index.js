import { createHistory } from 'history';
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import { IndexRoute, NotFound, Redirect, Router, Route } from 'react-router';

import App from './containers/App';
import configureStore from './store/configureStore';

const store = configureStore();

/**
 * All routes used in the application.
 */
const MyRouter = React.createClass({
  render: function() {
    return (
      <Router history={createHistory()}>
        <Redirect from="/" to="/app" />
        <Route path="/app" component={App}>
          <IndexRoute component={App}/>
          <Route path="*" component={NotFound} />
        </Route>
        <Route path="*" component={NotFound} />
      </Router>);
  }
});

render(
  <Provider store={store}>
    <MyRouter />
  </Provider>,
  document.getElementById('root')
);
