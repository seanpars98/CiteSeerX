<%@ page language="java"
	import="javax.naming.*,javax.rmi.PortableRemoteObject,java.util.*,java.io.*,java.sql.*,java.lang.*" %>
<%
	String name = (String) session.getAttribute("username");
	int userid = Integer.parseInt((String) session
			.getAttribute("userid"));
	String folder = request.getParameter("newfolder");

	Connection con = null;
	ResultSet rs = null;
	PreparedStatement ps = null;
	Statement sm = null;
	try {
		String mysqluser = "yasong";
		String mysqlpass = "";
		String url = "jdbc:mysql://localhost/citeseer";
		Class.forName("com.mysql.jdbc.Driver").newInstance();
		con = DriverManager.getConnection(url, mysqluser.toLowerCase(),
				mysqlpass.toLowerCase());
		int did = 0; //create dummy did which could never happen
		if (userid > 0) { // valid user id
			System.out.println("Connection Successful!");

			String updatefavourite = ("INSERT into favouritepapers "
					+ "(did, userid, folder) " + "values ('" + did
					+ "', '" + userid + "', '" + folder + "')");
			sm = con.createStatement();
			int r = sm.executeUpdate(updatefavourite);
			System.out.println("Insert Successful");
			response.sendRedirect("favouritepapers.jsp");
		} else {
			response.sendRedirect("error/loginfalse.html");
		}

	} catch (Exception e) {
		e.printStackTrace();
	}
%>

