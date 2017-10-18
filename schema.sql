CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id int  AUTO_INCREMENT,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    username VARCHAR(20),
    email varchar(255) UNIQUE,
    password varchar(255),
    DOB DATE,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Photos
(
  photoid int AUTO_INCREMENT,
  user_id int,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (photoid)
);

CREATE TABLE Owns_Albums
(
  user_id INT,
  album_id INT,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(album_id) REFERENCES Albums(albumID) ON DELETE CASCADE
);

CREATE TABLE Belongs_To
(
  photoID INT, albumID INT NOT NULL,
  PRIMARY KEY(photoID),
  FOREIGN KEY(photoID) REFERENCES Photos(photoid) ON DELETE CASCADE,
  FOREIGN KEY(albumID) REFERENCES Albums(albumID) ON DELETE CASCADE
);

CREATE TABLE Albums
(
  albumID INT AUTO_INCREMENT, albumOwner INT, name VARCHAR(30), datecreated DATE,
  PRIMARY KEY(albumID),
  FOREIGN KEY(albumOwner) references Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Comments
(
  commentID INT,
  text TEXT NOT NULL,
  userID INT,
  date DATE,
  PRIMARY KEY(commentID),
  FOREIGN KEY (userID) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Has_Comment
(
  commentID INT, photoid INT,
  PRIMARY KEY(commentID, photoid),
  FOREIGN KEY(commentID) REFERENCES Comments(commentID) ON DELETE CASCADE,
  FOREIGN KEY(photoid) REFERENCES Photos(photoid) ON DELETE CASCADE
);

CREATE TABLE Tags
(
  tag TINYTEXT NOT NULL,
  tagID int AUTO_INCREMENT,
  PRIMARY KEY (tagID)
);

CREATE TABLE Has_Tag
(
  tagID int, photoid INT,
  PRIMARY KEY(tagID, photoID),
  FOREIGN KEY(photoID) REFERENCES Photos(photoid) ON DELETE CASCADE,
  FOREIGN KEY(tagID) REFERENCES Tags(tagID) ON DELETE CASCADE
);

CREATE TABLE Friends
(
  userID1 INT NOT NULL,
  userID2 INT NOT NULL,
  PRIMARY KEY(userID1, userID2),
  FOREIGN KEY(userID1) REFERENCES USERS(user_id) ON DELETE CASCADE,
  FOREIGN KEY(userID2) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE Likes
(
  userID INT, photoID INT,
  PRIMARY KEY(userID, photoID),
  FOREIGN KEY(userID) REFERENCES Users(user_ID) ON DELETE CASCADE,
  FOREIGN KEY(photoID) REFERENCES Photos(photoID) ON DELETE CASCADE
);


INSERT INTO Users (firstname, lastname,username, email, password)
VALUES ('Yuta', 'Takano','test2','test2@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
