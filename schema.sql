CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    user_id int  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures
(
  picture_id int  AUTO_INCREMENT,
  user_id int,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Owns_Albums
(
  user_id INT,
  album_id INT,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(album_id) REFERENCES Albums(albumid) ON DELETE CASCADE
);

CREATE TABLE Belongs_To
(
  photoID INT, albumID INT NOT NULL,
  PRIMARY KEY(photoID),
  FOREIGN KEY(photoID) REFERENCES Photos(photoid) ON DELETE CASCADE,
  FOREIGN KEY(albumID) REFERENCES Albums(albumid) ON DELETE CASCADE
);

CREATE TABLE Belongs_To
(
  photoID INT, albumID INT NOT NULL,
  PRIMARY KEY(photoID),
  FOREIGN KEY(photoID) REFERENCES Photos(photoid) ON DELETE CASCADE,
  FOREIGN KEY(albumID) REFERENCES Albums(albumid) ON DELETE CASCADE
);

CREATE TABLE Albums
(
  albumID INT, name VARCHAR(30), datecreated DATE,
  PRIMARY KEY(albumID)
);

CREATE TABLE Comments
(
  commentID INT,
  text STRING NOT NULL,
  userID INT,
  date DATE,
  PRIMARY KEY(commentID),
  FOREIGN KEY (photoID) REFERENCES Photos(photoID) ON DELETE CASCADE
);

CREATE TABLE Has_Comment
(
  commentid INT, photoid INT,
  PRIMARY KEY(commentID, photoID),
  FOREIGN KEY(commentID) REFERENCES Comment(commentID) ON DELETE CASCADE,
  FOREIGN KEY(photoID) REFERENCES Photos(photoID) ON DELETE CASCADE
);

CREATE TABLE Tags
(
  tag STRING NOT NULL,
  PRIMARY KEY (tag)
);

CREATE TABLE Has_Tag
(
  tag STRING, photoid INT,
  PRIMARY KEY(tag, photoID),
  FOREIGN KEY(photoID) REFERENCES Photos(photoid) ON DELETE CASCADE
);

CREATE TABLE Friends
(
  userID INT,
  userID INT,
  PRIMARY KEY(userID, userID)
);

CREATE TABLE Likes
(
  userID INT, photoID INT,
  PRIMARY KEY(userID, photoID),
  FOREIGN KEY(userID) REFERENCES User(userID) ON DELETE CASCADE,
  FOREIGN KEY(photoID) REFERENCES Photo(photoID) ON DELETE CASCADE
);


INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
