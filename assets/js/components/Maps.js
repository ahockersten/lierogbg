import React, { Component } from 'react';

class MapItem extends Component {
  render() {
    const {name, author, description, file, img} = this.props;
    return (
      <div className="row">
        <div className="col-xs-3">
          <strong>{name}</strong> by <em>{author}</em><br/>
            {this.props.children}
        </div>
        <div className="col-xs-9">
          <a href={"/static/maps/"+file}>
            <img src={"/static/img/maps/"+img}></img>
          </a>
        </div>
      </div>
    );
  }
}

export class Maps extends Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12">
          <div className="row">
            <div className="col-xs-12">
              <h2>Maps</h2>
            </div>
          </div>
          <MapItem name="Pokol2" author="Biernath_John" img="pokol2.png"
                   file="pokol2.lev">
            <p>The staple map of the Polish League.</p>
          </MapItem>
          <MapItem name="Diamond" author="Errol Petersson (Errol)"
                   img="diamond.png" file="DIAMOND.LEV">
            Created in 2013.
            <p>A map with lots of lighting effects and cluster holes.</p>
          </MapItem>
          <MapItem name="Temple27" author="John Petersson (Poukah)"
                   img="TEMPLE27.png" file="TEMPLE27.LEV">
            Latest version from September 9, 2014.
            <p>
              A remake of the classic map <em>Temple</em> with no sand and
              several other alterations.
            </p>
            <p>
              The original designer is unknown but the map has lived through
              other incarnations since the beginning of the millennium.
            </p>
          </MapItem>
          <MapItem name="India2" author="Anton Melander (TommyGunn)"
                   img="INDIA2.png" file="INDIA2.LEV">
            Originally created in 2012.
            <p>Got a second version with bunny jumps on September 9, 2014.</p>
          </MapItem>
          <MapItem name="BEAM2" author="John Petersson (Poukah)"
                   img="BEAM2.png" file="BEAM2.LEV">
            First released in 2012. Latest version from September 9, 2014.
            <p>
              Inspired by the classic map <em>Stoneage</em> but without sand,
              thinner beams and a few loopholes.
            </p>
          </MapItem>
          <MapItem name="HUSK" author="John Petersson (Poukah)"
                   img="husk.png" file="HUSK.LEV">
            Released in April 2015.
            <p>A new non-symmetrical map which aims to be a future hit.</p>
          </MapItem>
        </div>
      </div>
    );
  }
}

export default Maps;
