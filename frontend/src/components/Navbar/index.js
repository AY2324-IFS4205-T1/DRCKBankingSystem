import React from "react";
import { Nav, NavLink, NavMenu }
    from "./NavbarElements";

const Navbar = () => {
    return (
        <>
            <Nav>
                <NavMenu>
                    <NavLink to="/" activeStyle>
                        Home
                    </NavLink>
                    <NavLink to="/apply" activeStyle>
                        Apply for Bank Accounts
                    </NavLink>
                    <NavLink to="/balance" activeStyle>
                        View Balance
                    </NavLink>
                    <NavLink to="/transfer" activeStyle>
                        Tranfer Funds
                    </NavLink>
                    <NavLink to="/atm" activeStyle>
                        ATM
                    </NavLink>
                    <NavLink to="/login" activeStyle>
                        Login/Logout
                    </NavLink>
                </NavMenu>
            </Nav>
        </>
    );
};

export default Navbar;