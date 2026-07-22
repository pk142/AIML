function MemeCard(props) {
  return (
    <div className="meme-card">
      <img src={props.imageUrl} alt={props.caption} width="300" />
      <p className="meme-caption" key={props.caption}>{props.caption}</p>
    </div>
  );
}

export default MemeCard;