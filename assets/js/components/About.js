import React, { Component } from 'react';

export class About extends Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12">
          <h2>About LieroGBG</h2>
          <p>
            LieroGBG is an organization located in Gothenburg, Sweden working
            for the proliferation of the game Liero
            (1.33 © Joosa Riekkinen, 1.36 © Erik Lindroos), first released
            in 1998.
          </p>
          <p>
            The activity around this specific community began with a few
            people in 2012, and have since seen a steady addition of players.
            In May of 2013, a ranking system - similar to the one used in
            Chess - for comparing skill levels between players worldwide, was
            launched.
          </p>
          <p>
            All results have been kept by manual bookkeeping, on paper, in
            spreadsheets and in stored game replays, but since September 2014,
            we are proud to present an automated system here on this site,
            where matches can be registered by filling in the results of local
            games and providing the replays for these, and the site will
            assemble the data into a comprehensible ranking list. More
            information on how this system works may be found under
            <a href="{% url 'rules.views.index' %}">rules</a>.
          </p>
          <p>
            The game is played on one computer (Linux, Windows, Mac), in split
            screen, on the keyboard and a common issue you may run in to is
            the fact that a lot of keyboards can't register too many keys
            simultaneously. It is therefore recommended to use a keyboard with
            good rollover, preferably a mechanical one.
          </p>
          <p>
            For download and installation instructions visit the official site
            <a href="http://www.liero.be">liero.be</a>.
          </p>
          <p>
            If you have questions about the game the expert panel can be found
            on IRC at:
            <a href="irc://irc.quakenet.org/liero">#liero@irc.quakenet.org</a>
            or you may turn to us with questions, suggestions and the like at
            <a href="mailto:lierogbg@gmail.com">lierogbg@gmail.com</a>.
          </p>
          <p>
            Enjoy!
          </p>
        </div>
      </div>
    );
  }
}

export default About;
