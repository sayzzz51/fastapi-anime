--
-- PostgreSQL database dump
--

\restrict V5WFAf39UK6PcDGCROpAMjbuc3p1L6xg09HSNWlqB3t0q846GIDFLfKDvxgcmFs

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anime; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anime (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    year integer NOT NULL,
    episodes integer NOT NULL,
    status character varying(50),
    CONSTRAINT anime_episodes_check CHECK ((episodes >= 1)),
    CONSTRAINT anime_status_check CHECK (((status)::text = ANY ((ARRAY['ongoing'::character varying, 'finished'::character varying, 'announced'::character varying])::text[]))),
    CONSTRAINT anime_year_check CHECK (((year >= 1960) AND (year <= 2030)))
);


--
-- Name: anime_genre; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anime_genre (
    anime_id integer NOT NULL,
    genre_id integer NOT NULL
);


--
-- Name: anime_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.anime_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: anime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.anime_id_seq OWNED BY public.anime.id;


--
-- Name: genres; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.genres (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: genres_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.genres_id_seq OWNED BY public.genres.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    anime_id integer,
    author character varying(50) NOT NULL,
    score integer NOT NULL,
    text character varying(1000),
    CONSTRAINT reviews_score_check CHECK (((score >= 1) AND (score <= 10)))
);


--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: anime id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime ALTER COLUMN id SET DEFAULT nextval('public.anime_id_seq'::regclass);


--
-- Name: genres id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.genres ALTER COLUMN id SET DEFAULT nextval('public.genres_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: anime_genre anime_genre_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_genre
    ADD CONSTRAINT anime_genre_pkey PRIMARY KEY (anime_id, genre_id);


--
-- Name: anime anime_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime
    ADD CONSTRAINT anime_pkey PRIMARY KEY (id);


--
-- Name: anime anime_title_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime
    ADD CONSTRAINT anime_title_key UNIQUE (title);


--
-- Name: genres genres_name_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_name_unique UNIQUE (name);


--
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: anime_genre anime_genre_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_genre
    ADD CONSTRAINT anime_genre_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- Name: anime_genre anime_genre_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_genre
    ADD CONSTRAINT anime_genre_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE CASCADE;


--
-- Name: reviews reviews_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.anime(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict V5WFAf39UK6PcDGCROpAMjbuc3p1L6xg09HSNWlqB3t0q846GIDFLfKDvxgcmFs

