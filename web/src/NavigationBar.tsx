/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';

declare type SwitchActiveViewCB = (activeView: string) => void;

type NavbarProps = {
  activeView: string;
  switchActiveViewCB: SwitchActiveViewCB;
};

export default class NavigationBar extends React.Component<NavbarProps, any> {
  onSelect(selectedKey: string | null) {
    const { switchActiveViewCB } = this.props;
    if (selectedKey) switchActiveViewCB(selectedKey);
  }

  render() {
    const { activeView } = this.props;
    return (
      <>
        <Navbar bg="dark" variant="dark" className="navbar-expand px-3">
          {/* <Navbar.Brand href="#"><i className="bi bi-bluetooth text-primary d-inline-block align-middle px-2" style={{ fontSize: '4.5rem' }} /><strong className="text-primary">RPI-K(V)M</strong></Navbar.Brand> */}
          {/* <a className="navbar-brand" href="#">RPI-K(V)M</a> */}
          <Nav
            className="me-auto"
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            {/* <Nav.Link eventKey="Home">Home</Nav.Link> */}
            <Nav.Link eventKey="Bt-Clients" className="me-auto">
              <i className="bi bi-bluetooth text-primary d-inline-block align-middle px-2" style={{ fontSize: '4.5rem' }} /><strong className="text-primary">RPI-K(V)M</strong>
              {/* Bt-Clients */}
            </Nav.Link>
          </Nav>
          <Nav
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            <Nav.Link eventKey="Settings" className="py-0">
              <i className="bi bi-gear-wide-connected text-secondary px-2" style={{ fontSize: '4.5rem' }} />
            </Nav.Link>
          </Nav>
        </Navbar>
      </>
    );
  }
}
