-- phpMyAdmin SQL Dump
-- version 4.2.11
-- http://www.phpmyadmin.net
--
-- Servidor: localhost
-- Tiempo de generación: 13-03-2015 a las 20:49:50
-- Versión del servidor: 5.6.21
-- Versión de PHP: 5.6.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de datos: `WAU`
--

DELIMITER $$
--
-- Procedimientos
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `Login`(IN `Email` TEXT, IN `PhoneNumber` TEXT, IN `GCMID` TEXT)
    DETERMINISTIC
BEGIN
    Set @ID = (Select User.ID from User where User.PhoneNumber = PhoneNumber);
    if(@ID is NULL)then
         INSERT INTO User (`PhoneNumber`, `Email`, `GCMID`) VALUES 	(PhoneNumber,Email,GCMID);
        Set @ID = LAST_INSERT_ID();
    END IF;
    Select @ID;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Message`
--

CREATE TABLE IF NOT EXISTS `Message` (
  `ID` int(11) NOT NULL,
  `SenderID` int(11) NOT NULL,
  `CreatedTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Message` text NOT NULL,
  `ReceiverID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `User`
--

CREATE TABLE IF NOT EXISTS `User` (
`ID` int(11) NOT NULL,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(100) DEFAULT NULL,
  `GCMID` text
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `User`
--

INSERT INTO `User` (`ID`, `PhoneNumber`, `Email`, `GCMID`) VALUES
(39, '0034653961314', 'jorgr.girabal@gmail.com', 'APA91bGufLmYIuMvz7uUh270pXKgGQrp0TLrrn7cuAWIhxiYb01uiS0Wo_CkkQxuHrmKR2DOw66OpEM_D7u88kqoYoOTXL4qY9B8qk62ASCMyDciIYFxv5kQaI0BLX_pf6cUlPeeIlA3gmMT_JBtEZCGlceSqAq8idYZ2yhvLniRO-xbvduR3bQ');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `User`
--
ALTER TABLE `User`
 ADD PRIMARY KEY (`ID`), ADD UNIQUE KEY `PhoneNumber` (`PhoneNumber`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `User`
--
ALTER TABLE `User`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=40;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
