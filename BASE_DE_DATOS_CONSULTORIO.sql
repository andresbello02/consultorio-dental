
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `citas`
--

DROP TABLE IF EXISTS `citas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `citas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `paciente_nombre` varchar(100) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `hora` varchar(20) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Pendiente',
  `servicio_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `fk_citas_servicios` (`servicio_id`),
  CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_citas_servicios` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `citas`
--

LOCK TABLES `citas` WRITE;
/*!40000 ALTER TABLE `citas` DISABLE KEYS */;
INSERT INTO `citas` VALUES (1,7,'Andres','2026-05-05','11:00 AM','Pendiente',NULL),(2,7,'Andres','2026-05-03','11:00 AM','Pendiente',NULL),(3,7,'Andres','2026-05-28','11:00 AM','Pendiente',NULL),(4,7,'Andres','2026-05-28','04:00 PM','Pendiente',NULL),(5,7,'Andres','2026-05-05','04:00 PM','Pendiente',NULL),(6,7,'daniel','2026-05-20','08:00 AM','Pendiente',NULL),(7,7,'daniel','2026-04-26','08:00 AM','Pendiente',NULL),(8,10,'Camila Pinzón Castro','2026-05-08','11:00 AM','Pendiente',NULL),(9,11,'garcia','2026-05-07','08:00 AM','Pendiente',NULL),(10,11,'Garcia','2025-10-06','08:00 AM','Pendiente',NULL),(11,11,'Garcia','2025-01-06','08:00 AM','Pendiente',NULL),(12,10,'Camila Pinzón Castro','2025-03-03','08:00 AM','Pendiente',NULL),(13,12,'Angie Valeria Ruiz Moreno','2026-05-22','11:00 AM','Pendiente',NULL),(14,12,'Angie Valeria Ruiz Moreno','2025-10-22','11:00 AM','Pendiente',NULL),(17,10,'oscar','2025-09-08','08:00 AM','Pendiente',NULL),(18,NULL,'prueba','2026-06-19','10:00 AM','Pendiente',NULL),(19,NULL,'prueba','2026-06-12','11:00 AM','Pendiente',NULL),(20,NULL,'prueba2','2026-06-12','10:00 AM','Pendiente',NULL),(21,NULL,'pruebaaaa','2026-06-12','09:00 AM','Pendiente',NULL),(22,NULL,'a','2025-05-11','08:00 AM','Pendiente',NULL),(23,15,'jesus','2026-06-12','08:00 AM','Pendiente',NULL),(24,27,'andres','2027-12-01','10:00 AM','Pendiente',NULL),(25,27,'andres','2026-08-09','03:00 PM','Pendiente',NULL),(26,27,'andres','2026-08-27','02:00 PM','Pendiente',NULL),(27,27,'andres','2026-09-01','08:00 AM','Pendiente',NULL),(28,27,'prueba123','2026-08-07','08:00 AM','Pendiente',NULL),(29,27,'angel','2026-08-31','11:00 AM','Pendiente',NULL);
/*!40000 ALTER TABLE `citas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contactos`
--

DROP TABLE IF EXISTS `contactos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contactos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(150) NOT NULL,
  `interes` varchar(100) NOT NULL,
  `mensaje` text,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contactos`
--

LOCK TABLES `contactos` WRITE;
/*!40000 ALTER TABLE `contactos` DISABLE KEYS */;
/*!40000 ALTER TABLE `contactos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opiniones`
--

DROP TABLE IF EXISTS `opiniones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opiniones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `calificacion` int NOT NULL,
  `comentario` text NOT NULL,
  `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `opiniones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opiniones`
--

LOCK TABLES `opiniones` WRITE;
/*!40000 ALTER TABLE `opiniones` DISABLE KEYS */;
INSERT INTO `opiniones` VALUES (1,16,5,'Excelente experiencia','2026-08-12 22:13:49'),(2,16,4,'Faltan mas consultorios','2026-08-12 22:14:08');
/*!40000 ALTER TABLE `opiniones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES (1,'Consulta General','Evaluación clínica y diagnóstico oral completo',1),(2,'Blanqueamiento Dental','Tratamiento estético de aclaramiento dental',1),(3,'Ortodoncia','Instalación y ajuste de brackets cerámicos o metálicos',1),(4,'Diseño de Sonrisa','Restauración estética personalizada',1),(5,'Implantes Dentales','Reconstrucción fija de piezas dentales',1),(6,'Consulta General','Evaluación y diagnóstico odontológico general.',1),(7,'Blanqueamiento Dental','Tratamiento estético para aclarar el tono de las piezas dentales.',1),(8,'Ortodoncia','Instalación y ajuste de brackets para alineación dental.',1),(9,'Limpieza Profiláctica','Limpieza profunda para remover sarro y placa bacteriana.',1),(10,'Consulta General','Evaluación y diagnóstico odontológico general.',1),(11,'Blanqueamiento Dental','Tratamiento estético para aclarar el tono de las piezas dentales.',1),(12,'Ortodoncia','Instalación y ajuste de brackets para alineación dental.',1),(13,'Limpieza Profiláctica','Limpieza profunda para remover sarro y placa bacteriana.',1),(14,'Consulta General','Evaluación y diagnóstico odontológico general.',1),(15,'Blanqueamiento Dental','Tratamiento estético para aclarar el tono dental.',1),(16,'Limpieza Profiláctica','Limpieza profunda para remover placa y sarro.',1),(17,'Consulta General','Evaluación y diagnóstico odontológico general.',1),(18,'Blanqueamiento Dental','Tratamiento estético para aclarar el tono dental.',1),(19,'Limpieza Profiláctica','Limpieza profunda para remover placa y sarro.',1),(20,'Consulta General','Evaluación y diagnóstico odontológico general.',1),(21,'Blanqueamiento Dental','Tratamiento estético para aclarar el tono dental.',1),(22,'Limpieza Profiláctica','Limpieza profunda para remover placa y sarro.',1);
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `rol` varchar(20) DEFAULT 'paciente',
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_exp` datetime DEFAULT NULL,
  `codigo_2fa` varchar(6) DEFAULT NULL,
  `codigo_2fa_exp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Samuel Solorzano','samuel_solorzanobravost@gmail.com','scrypt:32768:8:1$GKPGBoHUaQewMsbL$ce9f1a1024b00aa41f42c5e4e98791ecc9912ef7abe499443794b3d37f94adabad09ecd14cd7da40ff85db497792ba5a29d3538c6a37fa7d2fc4895a48a0bb69','paciente',NULL,NULL,NULL,NULL),(3,'dniel','camila_pinzoncastrost@gmail.com','scrypt:32768:8:1$uuvVBYFSOD82kSVV$a5986ee16baed0d7670dd6948a06f3aa98e0b1ee2b1baf984033722c0f562884f9475f3f22b6ce11b5aa5b869243439da86565d6fb31685263f1cf0029c40f9e','paciente',NULL,NULL,NULL,NULL),(4,'garcia','oncastrost@gmail.com','scrypt:32768:8:1$wn8UKyJBv1sDdjwG$952e0da288088146d453f540d2086d9efea2e4ac6a6900a244933650789d92981af69a023143aa28f96daad769d285c754d5e9dae2c7d6b4800de24f62f75e2f','paciente',NULL,NULL,NULL,NULL),(5,'Andres','asd@gmail.com','scrypt:32768:8:1$uz9kFD2N9eV2xat0$14e7b2162178375bffca28b280cfce1ba977f0d7ec87881085f25ab545839195441edf91daa36e0f718cce31ec47ed36bec4929896b5f13f0ca78f06f4c6296f','paciente',NULL,NULL,NULL,NULL),(6,'Andres','andresbello@gmail.com','scrypt:32768:8:1$sP5jGhdk7UvmgXBY$592f14db26a63eda6f615ddaec89d56158731d5a356f227159522eb393a9384d8c4e0e71f4d8aa936d420721f83741a7cd15c044f9fd50d9e16b6211d86a0a6d','paciente',NULL,NULL,NULL,NULL),(7,'andres','bello@gmail.com','scrypt:32768:8:1$AzO4CwhfNmS3Rwg1$903f686f35611713340796ddf9fb534895f6bdcbddab07cc3c852f027b6f8b81cf7fbabff239a825e6fd07e1a40a5bd25a8710bbf5893277a15d7bbae98ed97d','paciente',NULL,NULL,NULL,NULL),(8,'camilo','camilo@gmail.com','scrypt:32768:8:1$Ynivq4P9FEEMi44w$065dff9ddd96855b872a3b94c439893a1997c0e900bc3ef9b85ce3db9930945bd0c7ab0bfc6c5c011855d8b39c33c3620c11eb9d7ee0d4593ec0b3ee08e81e22','paciente',NULL,NULL,NULL,NULL),(9,'admin@consultorio.com','admin@consultorio.com','scrypt:32768:8:1$G326iMObRKrAL8GP$04cbfbfcdf04254e87b655887bac6201505c48e2c5059f63d78529dfb8f63e693907be20a74b9eb36dfddbd657724d26175eb533ded6fa565cb37ab7cb9f5d81','paciente',NULL,NULL,NULL,NULL),(10,'cami','maria_pinzonst@gfc.edu.co','scrypt:32768:8:1$8Xbk25uAiyGe1M9p$41cc4b9e8e12392c317429891866acf3ebc52617c38958fe11fa1ffaa2cb10a3a32515b1e173190e7a3e153e211c2ad0dbd2ccbe6d203d993ea30aebaaf73f67','paciente',NULL,NULL,NULL,NULL),(11,'garcia','garcia@gmail.com','scrypt:32768:8:1$7Kr9DwDEU6U6NtFs$bdf562e50db9856e277d7d3e01cb8fe89f35f0b8d699c7741c5ceab0bfac81160c30e0755bb1f4e52dd03bba6b53a6b0d09227fb375c6399290ce7ce724ef37e','paciente',NULL,NULL,NULL,NULL),(12,'Angie_ruiz','angie_ruizst@gfc.edu.co','scrypt:32768:8:1$pPHhto3PO9lX8GRM$71ff139d8125364d7264922d38952e6f9353c21722fdda193b0acde64a7fc8cb43247462c0cf18ff8e7ce6f35aeaaff34aeef154cd93c09232527f2f9bf04ebe','paciente',NULL,NULL,NULL,NULL),(13,'hola','hola@gmail.com','scrypt:32768:8:1$GhUZ8walKNChyzxZ$babc495c17c004b9ba69789a3afcfc391c1bc89185f18553998cd284db74755172d5d9c01ae02106e464610053d6cb6360ed4d781e78346cc5539cac1dbaff18','paciente',NULL,NULL,NULL,NULL),(14,'holaa','holaa@gmail.com','scrypt:32768:8:1$7CehwXrLBvcWaXgy$382b34cffc262643f98c2f5f2995ec459053e5e7b0fc77cf50c16bddda66010e35748907593640dad0f5ba1e9fb5ece6f2ed5dc4dce2c4f3d5ff9545cd5bdaa7','paciente',NULL,NULL,NULL,NULL),(15,'p','p@gmail.com','scrypt:32768:8:1$0QCitlf0xxlSBPUp$3522893249ffa3cd59c369eb47bf284f09d3a85623843527c9d7fdc86478d9e6d69b14f0cea32a9e8a416f09af14da9072465849f51c72e8056f292abe3bba01','paciente',NULL,NULL,NULL,NULL),(16,'andres','andres@gmail.com','scrypt:32768:8:1$B9sKACeZQU1U7QXF$258f03c7359483c0f0db3a43b79f6bb7d37bbbd3e2bf83b4daaa5a90bd0f502f338337f631d52a5f58bd861ce6e91173e0dc2227d83b076f057fca51fd80919c','paciente',NULL,NULL,NULL,NULL),(19,'andres','andres_belloruizst@gfc.edu.co','scrypt:32768:8:1$UMe74LHK16PyCEEM$96994f8e312dfd5be4b8578ee8afeaa6da6415b89253afca09b4ac0db952baf98953fb9708ea6d8c1976034810a82c53a0cdd74ef5a88bd711a0dfb06e2823da','admin',NULL,NULL,NULL,NULL),(26,'andres123','andresbelloruiz02@gmail.com','scrypt:32768:8:1$2RcfQbT3PzHLwa1o$9a5f15172e463307541142c2dd16ef4c1f367dc6167020a7ab494f5156bcbe70e341a98cf0fcfc19fd7773f2c5abdee4e108e2050b01fa30e08dd956e3e5da2a','admin','jFaYPcxUxoMnXAf-NXzMKSFAhaxp9Lwb_hW6IbyXnCQ','2026-08-30 22:13:34','167364','2026-08-30 22:35:08'),(27,'prueba123','prueba111@gmail.com','scrypt:32768:8:1$ZsQU393xNnqbXZK9$5f9732d195c700d9b4c2bc0e1d62b73a8bf61547dc1fc5bc3fd78436fbd95a0878c33c1b90fc9291d30c190dd2db1c4b4070c7deea6475da2bfcf349e3b6a384','paciente',NULL,NULL,NULL,NULL),(28,'majo','majo@gmail.com','scrypt:32768:8:1$ysM2EK4SPScfARXi$aca8fa712e7dc898278fae6cbfb22bf239ac3a337faa136fb787a546fefbd377e04e273c9a39b210798a68c346152eb40aa99dee321b125c279d825da8c17143','paciente',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;